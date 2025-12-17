"""Fetch performance reports from Amazon Ads API.

This module handles fetching keyword performance data from the Amazon Ads API
and storing it in the database.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import date
from typing import Optional

from agent.api.amazon_ads_client import get_client
from agent.data import dao
from agent.jobs.job_tracker import JobStatus, get_tracker

logger = logging.getLogger(__name__)


class SimplePerformanceRecord:
    """Simple object to hold performance data for dao.upsert_performance."""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


def parse_amazon_record_to_performance(
    record: dict,
    profile_id: str,
    report_date: date,
) -> SimplePerformanceRecord:
    """Parse Amazon Ads API record to performance data structure.

    Args:
        record: Raw record from Amazon Ads API
        profile_id: Amazon profile ID
        report_date: Date of the report

    Returns:
        SimplePerformanceRecord instance
    """
    return SimplePerformanceRecord(
        keyword_id=str(record.get("keywordId", "unknown")),
        keyword_text=record.get("keywordText", ""),
        match_type=record.get("matchType", "UNKNOWN"),
        campaign_id=str(record.get("campaignId", "")),
        campaign_name=record.get("campaignName", ""),
        ad_group_id=str(record.get("adGroupId", "")),
        ad_group_name=record.get("adGroupName", ""),
        date=report_date,
        impressions=int(record.get("impressions", 0)),
        clicks=int(record.get("clicks", 0)),
        spend=float(record.get("cost", 0.0)),
        sales=float(record.get("attributedSales14d", 0.0)),
        orders=int(record.get("attributedConversions14d", 0)),
        units_sold=int(record.get("attributedUnitsOrdered14d", 0)),
        state=record.get("state", "UNKNOWN"),
        bid=float(record.get("bid", 0.0)) if record.get("bid") else None,
    )


async def fetch_reports_async(
    job_id: str,
    profile_id: str,
    start_date: date,
    end_date: date,
    report_type: str = "KEYWORDS"
) -> None:
    """Fetch reports from Amazon Ads API asynchronously.

    This function:
    1. Authenticates with Amazon Ads API
    2. Requests a keyword performance report
    3. Polls for report completion
    4. Downloads the report data
    5. Parses and stores records in the database

    Args:
        job_id: Unique job identifier for tracking
        profile_id: Amazon Ads profile ID
        start_date: Start date for report data
        end_date: End date for report data
        report_type: Type of report to fetch (default: KEYWORDS)
    """
    tracker = get_tracker()

    try:
        # Update job to in_progress
        await tracker.update_job(job_id, status=JobStatus.IN_PROGRESS, progress=0.0)
        logger.info(f"Starting Amazon Ads API fetch job {job_id} for profile {profile_id}")

        # Get Amazon Ads API client
        client = get_client()

        # Request and fetch the report
        await tracker.update_job(job_id, progress=10.0)
        logger.info(f"Requesting keyword report from {start_date} to {end_date}")

        # Fetch keyword report (this handles request, polling, and download)
        records = await client.fetch_keyword_report(
            start_date=start_date,
            end_date=end_date,
            max_wait_seconds=600.0,  # 10 minutes max
        )

        await tracker.update_job(job_id, progress=60.0, records_fetched=len(records))
        logger.info(f"Downloaded {len(records)} records from Amazon Ads API")

        # Parse records to PerformanceData models
        performance_records = []
        for record in records:
            try:
                perf_data = parse_amazon_record_to_performance(
                    record,
                    profile_id=profile_id,
                    report_date=end_date,  # Use end_date as the report date
                )
                performance_records.append(perf_data)
            except Exception as parse_error:
                logger.warning(f"Failed to parse record {record}: {parse_error}")
                continue

        await tracker.update_job(job_id, progress=80.0)
        logger.info(f"Parsed {len(performance_records)} performance records")

        # Store in database
        if performance_records:
            rows_added = dao.upsert_performance(performance_records, profile_id=profile_id)
            logger.info(f"Stored {rows_added} records in database")
        else:
            rows_added = 0
            logger.warning("No records to store")

        # Mark as completed
        await tracker.update_job(
            job_id,
            status=JobStatus.COMPLETED,
            progress=100.0,
            records_fetched=len(records)
        )

        logger.info(
            f"Completed fetch job {job_id}: {len(records)} records fetched, "
            f"{rows_added} stored from {start_date} to {end_date}"
        )

    except asyncio.TimeoutError:
        await tracker.update_job(
            job_id,
            status=JobStatus.TIMEOUT,
            error="Amazon Ads API report timed out"
        )
        logger.error(f"Fetch job {job_id} timed out waiting for report")

    except Exception as exc:
        error_msg = f"{type(exc).__name__}: {str(exc)}"
        await tracker.update_job(
            job_id,
            status=JobStatus.FAILED,
            error=error_msg
        )
        logger.error(f"Fetch job {job_id} failed: {error_msg}", exc_info=True)


def run(days: int = 30, job_id: Optional[str] = None) -> None:
    """Synchronous entry point for CLI.

    This is called by the CLI command. For now, it just logs a message.
    The async version is used by the API endpoints.

    Args:
        days: Number of days to fetch (default: 30)
        job_id: Optional job ID for tracking
    """
    logger.info(f"Fetch reports job requested for last {days} days")
    print(f"⚠️  CLI fetch not yet implemented. Use API endpoint: POST /api/fetch")
    print(f"   Job ID: {job_id}")
    print(f"   Days: {days}")
    print(f"\n   Example:")
    print(f"   curl -X POST http://localhost:8000/api/fetch \\")
    print(f'     -H "Content-Type: application/json" \\')
    print(f'     -d \'{{"profile_id": "your_profile_id", "start_date": "2025-11-01", "end_date": "2025-11-30", "report_type": "KEYWORDS"}}\'')
