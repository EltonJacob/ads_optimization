"""Data Access Object (DAO) for database operations.

This module provides database access functions.
Full implementation pending database models creation.
"""

from __future__ import annotations

import logging
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import List, Optional

logger = logging.getLogger(__name__)

# In-memory storage for mock implementation
_performance_data_store: List[dict] = []


def upsert_performance(records: List) -> int:
    """Upsert performance records to database.

    This is a placeholder implementation that stores data in memory.

    Args:
        records: List of KeywordPerformance records to persist

    Returns:
        Number of rows persisted
    """
    logger.info(f"Storing {len(records)} performance records in memory")

    # Convert records to dictionaries and store
    for record in records:
        record_dict = {
            "keyword_id": record.keyword_id,
            "date": record.date,
            "impressions": record.impressions,
            "clicks": record.clicks,
            "spend": record.spend,
            "sales": record.sales,
            "orders": record.orders,
            "created_at": datetime.now(),
        }
        _performance_data_store.append(record_dict)

    logger.info(f"Total records in store: {len(_performance_data_store)}")
    return len(records)


def query_performance(
    profile_id: str,
    start_date: date,
    end_date: date,
    campaign_id: Optional[int] = None,
    ad_group_id: Optional[int] = None,
    match_type: Optional[str] = None,
    keyword_state: Optional[str] = None,
) -> List[dict]:
    """Query performance data with filters.

    Args:
        profile_id: Amazon Ads profile ID
        start_date: Start date for query
        end_date: End date for query
        campaign_id: Optional campaign filter
        ad_group_id: Optional ad group filter
        match_type: Optional match type filter (exact, phrase, broad)
        keyword_state: Optional keyword state filter (enabled, paused, archived)

    Returns:
        List of performance records
    """
    logger.info(
        f"Querying performance data for profile {profile_id} "
        f"from {start_date} to {end_date}"
    )

    # Filter by date range
    filtered_data = [
        record
        for record in _performance_data_store
        if start_date <= record["date"] <= end_date
    ]

    logger.info(f"Found {len(filtered_data)} records in date range")
    return filtered_data


def get_performance_summary(
    profile_id: str,
    start_date: date,
    end_date: date,
) -> dict:
    """Get aggregated performance summary.

    Args:
        profile_id: Amazon Ads profile ID
        start_date: Start date for summary
        end_date: End date for summary

    Returns:
        Dictionary with aggregated metrics
    """
    data = query_performance(profile_id, start_date, end_date)

    if not data:
        return {
            "total_spend": Decimal("0"),
            "total_sales": Decimal("0"),
            "total_orders": 0,
            "total_impressions": 0,
            "total_clicks": 0,
            "avg_acos": None,
            "avg_roas": None,
            "avg_ctr": None,
            "keyword_count": 0,
        }

    total_spend = sum(Decimal(str(r["spend"])) for r in data)
    total_sales = sum(Decimal(str(r["sales"])) for r in data)
    total_orders = sum(r["orders"] for r in data)
    total_impressions = sum(r["impressions"] for r in data)
    total_clicks = sum(r["clicks"] for r in data)

    # Calculate averages
    avg_acos = (total_spend / total_sales * 100) if total_sales > 0 else None
    avg_roas = (total_sales / total_spend) if total_spend > 0 else None
    avg_ctr = (Decimal(total_clicks) / Decimal(total_impressions) * 100) if total_impressions > 0 else None

    # Count unique keywords
    unique_keywords = len(set(r["keyword_id"] for r in data))

    return {
        "total_spend": total_spend,
        "total_sales": total_sales,
        "total_orders": total_orders,
        "total_impressions": total_impressions,
        "total_clicks": total_clicks,
        "avg_acos": round(avg_acos, 2) if avg_acos else None,
        "avg_roas": round(avg_roas, 2) if avg_roas else None,
        "avg_ctr": round(avg_ctr, 2) if avg_ctr else None,
        "keyword_count": unique_keywords,
    }


def query_keywords(
    profile_id: str,
    start_date: date,
    end_date: date,
    page: int = 1,
    page_size: int = 50,
    sort_by: str = "spend",
    sort_order: str = "desc",
) -> tuple[List[dict], int]:
    """Query keyword-level performance with pagination and sorting.

    Args:
        profile_id: Amazon Ads profile ID
        start_date: Start date for query
        end_date: End date for query
        page: Page number (1-indexed)
        page_size: Number of results per page
        sort_by: Field to sort by (spend, sales, clicks, impressions, acos)
        sort_order: Sort order (asc, desc)

    Returns:
        Tuple of (keyword_list, total_count)
    """
    data = query_performance(profile_id, start_date, end_date)

    # Group by keyword_id
    keyword_map = {}
    for record in data:
        kid = record["keyword_id"]
        if kid not in keyword_map:
            keyword_map[kid] = {
                "keyword_id": kid,
                "keyword_text": f"keyword_{kid}",
                "match_type": "exact",
                "campaign_name": "Mock Campaign",
                "ad_group_name": "Mock Ad Group",
                "state": "enabled",
                "bid": Decimal("0.50"),
                "impressions": 0,
                "clicks": 0,
                "spend": Decimal("0"),
                "sales": Decimal("0"),
                "orders": 0,
            }

        keyword_map[kid]["impressions"] += record["impressions"]
        keyword_map[kid]["clicks"] += record["clicks"]
        keyword_map[kid]["spend"] += Decimal(str(record["spend"]))
        keyword_map[kid]["sales"] += Decimal(str(record["sales"]))
        keyword_map[kid]["orders"] += record["orders"]

    # Calculate metrics for each keyword
    keywords = []
    for kw in keyword_map.values():
        spend = kw["spend"]
        sales = kw["sales"]
        clicks = kw["clicks"]
        impressions = kw["impressions"]

        kw["cpc"] = (spend / Decimal(clicks)) if clicks > 0 else None
        kw["ctr"] = (Decimal(clicks) / Decimal(impressions) * 100) if impressions > 0 else None
        kw["acos"] = (spend / sales * 100) if sales > 0 else None
        kw["roas"] = (sales / spend) if spend > 0 else None
        kw["conversion_rate"] = (Decimal(kw["orders"]) / Decimal(clicks) * 100) if clicks > 0 else None

        keywords.append(kw)

    # Sort
    reverse = sort_order == "desc"
    if sort_by in keywords[0] if keywords else []:
        keywords.sort(key=lambda x: x.get(sort_by, 0) or 0, reverse=reverse)

    total_count = len(keywords)

    # Paginate
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated = keywords[start_idx:end_idx]

    return paginated, total_count


def query_trends(
    profile_id: str,
    start_date: date,
    end_date: date,
    group_by: str = "day",
) -> List[dict]:
    """Query trend data grouped by time period.

    Args:
        profile_id: Amazon Ads profile ID
        start_date: Start date for trends
        end_date: End date for trends
        group_by: Grouping period (day, week, month)

    Returns:
        List of trend data points
    """
    data = query_performance(profile_id, start_date, end_date)

    # Group by date
    date_map = {}
    for record in data:
        record_date = record["date"]

        # Adjust grouping
        if group_by == "week":
            # Group by week start (Monday)
            record_date = record_date - timedelta(days=record_date.weekday())
        elif group_by == "month":
            # Group by month start
            record_date = record_date.replace(day=1)

        if record_date not in date_map:
            date_map[record_date] = {
                "date": record_date,
                "impressions": 0,
                "clicks": 0,
                "spend": Decimal("0"),
                "sales": Decimal("0"),
                "orders": 0,
            }

        date_map[record_date]["impressions"] += record["impressions"]
        date_map[record_date]["clicks"] += record["clicks"]
        date_map[record_date]["spend"] += Decimal(str(record["spend"]))
        date_map[record_date]["sales"] += Decimal(str(record["sales"]))
        date_map[record_date]["orders"] += record["orders"]

    # Calculate metrics
    trends = []
    for trend in date_map.values():
        spend = trend["spend"]
        sales = trend["sales"]
        clicks = trend["clicks"]
        impressions = trend["impressions"]

        trend["acos"] = (spend / sales * 100) if sales > 0 else None
        trend["roas"] = (sales / spend) if spend > 0 else None
        trend["ctr"] = (Decimal(clicks) / Decimal(impressions) * 100) if impressions > 0 else None

        trends.append(trend)

    # Sort by date
    trends.sort(key=lambda x: x["date"])

    return trends


def get_data_sources(
    profile_id: str,
    start_date: date,
    end_date: date,
) -> dict:
    """Get information about data sources by date range.

    Args:
        profile_id: Amazon Ads profile ID
        start_date: Start date for query
        end_date: End date for query

    Returns:
        Dictionary with data source information
    """
    # Mock implementation - in real version, would track source in database
    total_records = len(query_performance(profile_id, start_date, end_date))

    return {
        "profile_id": profile_id,
        "sources": [
            {
                "start_date": start_date,
                "end_date": end_date,
                "source": "upload",
                "record_count": total_records,
            }
        ],
        "total_records": total_records,
        "api_records": 0,
        "upload_records": total_records,
        "date_range_start": start_date,
        "date_range_end": end_date,
    }
