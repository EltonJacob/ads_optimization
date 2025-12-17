"""Amazon Ads API Client.

This module provides a client for interacting with the Amazon Advertising API,
specifically for fetching Sponsored Products keyword performance reports.
"""

from __future__ import annotations

import asyncio
import logging
import time
from datetime import date, datetime
from typing import Any, Dict, List, Optional

import httpx

from agent.api.config import config

logger = logging.getLogger(__name__)


class AmazonAdsAPIClient:
    """Client for Amazon Advertising API with async support."""

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        refresh_token: Optional[str] = None,
        profile_id: Optional[str] = None,
    ):
        """Initialize the Amazon Ads API client.

        Args:
            client_id: OAuth 2.0 client ID (defaults to config)
            client_secret: OAuth 2.0 client secret (defaults to config)
            refresh_token: OAuth 2.0 refresh token (defaults to config)
            profile_id: Amazon Ads profile ID (defaults to config)
        """
        self.client_id = client_id or config.client_id
        self.client_secret = client_secret or config.client_secret
        self.refresh_token = refresh_token or config.refresh_token
        self.profile_id = profile_id or config.profile_id

        self.api_base = config.api_base
        self.auth_url = config.auth_url

        self.access_token: Optional[str] = None
        self.token_expires_at: float = 0

        # HTTP client for async requests
        self.http_client = httpx.AsyncClient(timeout=30.0)

    async def _get_access_token(self) -> str:
        """Get or refresh access token.

        Returns:
            Valid access token

        Raises:
            Exception: If token refresh fails
        """
        # Check if token is still valid (with 5 min buffer)
        if self.access_token and time.time() < (self.token_expires_at - 300):
            return self.access_token

        logger.info("Refreshing Amazon Ads API access token")

        # Request new token
        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        response = await self.http_client.post(self.auth_url, data=data)
        response.raise_for_status()

        token_data = response.json()
        self.access_token = token_data["access_token"]
        expires_in = token_data.get("expires_in", 3600)
        self.token_expires_at = time.time() + expires_in

        logger.info(f"Access token refreshed, expires in {expires_in} seconds")
        return self.access_token

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Make an authenticated API request.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional arguments for httpx request

        Returns:
            JSON response data

        Raises:
            httpx.HTTPStatusError: If request fails
        """
        token = await self._get_access_token()

        headers = {
            "Authorization": f"Bearer {token}",
            "Amazon-Advertising-API-ClientId": self.client_id,
            "Amazon-Advertising-API-Scope": self.profile_id,
            "Content-Type": "application/json",
        }

        url = f"{self.api_base}{endpoint}"
        response = await self.http_client.request(method, url, headers=headers, **kwargs)
        response.raise_for_status()

        return response.json()

    async def request_report(
        self,
        report_type: str,
        start_date: date,
        end_date: date,
        metrics: Optional[List[str]] = None,
    ) -> str:
        """Request a performance report from Amazon Ads API.

        Args:
            report_type: Type of report (e.g., "spKeywords", "spCampaigns")
            start_date: Start date for report data
            end_date: End date for report data
            metrics: List of metrics to include (optional)

        Returns:
            Report ID for polling

        Raises:
            Exception: If report request fails
        """
        logger.info(f"Requesting {report_type} report from {start_date} to {end_date}")

        # Default metrics for keyword reports
        if metrics is None:
            metrics = [
                "impressions",
                "clicks",
                "cost",
                "attributedConversions14d",
                "attributedSales14d",
                "attributedUnitsOrdered14d",
            ]

        payload = {
            "reportDate": end_date.isoformat(),
            "metrics": ",".join(metrics),
            "configuration": {
                "adProduct": "SPONSORED_PRODUCTS",
                "groupBy": ["keyword"],
                "columns": metrics,
                "reportTypeId": report_type,
                "timeUnit": "SUMMARY",
                "format": "JSON",
            }
        }

        # Create report request
        response = await self._make_request(
            "POST",
            f"/v2/sp/keywords/report",
            json=payload
        )

        report_id = response.get("reportId")
        if not report_id:
            raise Exception(f"Failed to get report ID from response: {response}")

        logger.info(f"Report requested successfully, ID: {report_id}")
        return report_id

    async def get_report_status(self, report_id: str) -> Dict[str, Any]:
        """Check the status of a report.

        Args:
            report_id: Report ID from request_report()

        Returns:
            Report status data including status and location

        Raises:
            Exception: If status check fails
        """
        response = await self._make_request("GET", f"/v2/reports/{report_id}")
        return response

    async def download_report(self, report_url: str) -> List[Dict[str, Any]]:
        """Download report data from the provided URL.

        Args:
            report_url: URL to download report (from get_report_status)

        Returns:
            List of report records

        Raises:
            Exception: If download fails
        """
        logger.info(f"Downloading report from {report_url}")

        response = await self.http_client.get(report_url)
        response.raise_for_status()

        data = response.json()
        logger.info(f"Downloaded {len(data)} records")
        return data

    async def fetch_keyword_report(
        self,
        start_date: date,
        end_date: date,
        max_wait_seconds: float = 600.0,
    ) -> List[Dict[str, Any]]:
        """Fetch keyword performance report with automatic polling.

        This is a high-level method that requests a report, polls for completion,
        and downloads the data.

        Args:
            start_date: Start date for report
            end_date: End date for report
            max_wait_seconds: Maximum time to wait for report (default: 10 minutes)

        Returns:
            List of keyword performance records

        Raises:
            TimeoutError: If report doesn't complete in time
            Exception: If report fails or download fails
        """
        # Request report
        report_id = await self.request_report("spKeywords", start_date, end_date)

        # Poll for completion
        start_time = time.time()
        poll_interval = 5.0  # seconds

        while True:
            elapsed = time.time() - start_time
            if elapsed > max_wait_seconds:
                raise TimeoutError(f"Report {report_id} did not complete within {max_wait_seconds} seconds")

            # Check status
            status_data = await self.get_report_status(report_id)
            status = status_data.get("status")

            logger.info(f"Report {report_id} status: {status}")

            if status == "SUCCESS":
                # Report is ready, download it
                report_url = status_data.get("location")
                if not report_url:
                    raise Exception(f"Report succeeded but no download location provided: {status_data}")

                return await self.download_report(report_url)

            elif status in ["FAILURE", "FAILED"]:
                raise Exception(f"Report {report_id} failed: {status_data}")

            elif status in ["IN_PROGRESS", "PENDING"]:
                # Wait and retry
                await asyncio.sleep(poll_interval)
                continue

            else:
                logger.warning(f"Unknown report status: {status}, continuing to poll")
                await asyncio.sleep(poll_interval)

    async def close(self):
        """Close the HTTP client."""
        await self.http_client.aclose()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()


# Singleton instance
_client: Optional[AmazonAdsAPIClient] = None


def get_client() -> AmazonAdsAPIClient:
    """Get or create the global Amazon Ads API client.

    Returns:
        AmazonAdsAPIClient instance
    """
    global _client
    if _client is None:
        _client = AmazonAdsAPIClient()
    return _client
