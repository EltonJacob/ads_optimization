"""Data Access Object (DAO) for database operations.

This module provides database access functions using PostgreSQL.
"""

from __future__ import annotations

import logging
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import and_, func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.orm import Session

from agent.database.connection import get_sync_session, IS_SQLITE
from agent.database.models import PerformanceData

logger = logging.getLogger(__name__)


def upsert_performance(records: List, profile_id: str = None) -> int:
    """Upsert performance records to PostgreSQL database.

    Args:
        records: List of performance records to persist
        profile_id: Amazon Ads profile ID (extracted from records if not provided)

    Returns:
        Number of rows persisted
    """
    if not records:
        logger.warning("No records to upsert")
        return 0

    logger.info(f"Storing {len(records)} performance records in PostgreSQL")

    session = get_sync_session()
    try:
        rows_added = 0

        for record in records:
            # Extract profile_id from record if not provided
            if profile_id is None:
                profile_id = getattr(record, "profile_id", None)
                if not profile_id:
                    logger.warning("No profile_id found in record, skipping")
                    continue

            # Prepare record data
            record_data = {
                "keyword_id": str(getattr(record, "keyword_id", "unknown")),
                "keyword_text": getattr(record, "keyword_text", ""),
                "match_type": getattr(record, "match_type", "UNKNOWN"),
                "campaign_id": str(getattr(record, "campaign_id", "")) if getattr(record, "campaign_id", None) else None,
                "campaign_name": getattr(record, "campaign_name", None),
                "ad_group_id": str(getattr(record, "ad_group_id", "")) if getattr(record, "ad_group_id", None) else None,
                "ad_group_name": getattr(record, "ad_group_name", None),
                "profile_id": str(profile_id),
                "state": getattr(record, "state", None),
                "bid": Decimal(str(getattr(record, "bid"))) if getattr(record, "bid", None) else None,
                "date": record.date,
                "impressions": int(getattr(record, "impressions", 0)),
                "clicks": int(getattr(record, "clicks", 0)),
                "spend": Decimal(str(getattr(record, "spend", 0))),
                "sales": Decimal(str(getattr(record, "sales", 0))),
                "orders": int(getattr(record, "orders", 0)),
                "units_sold": int(getattr(record, "units_sold", 0)),
                "source": getattr(record, "source", "api"),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }

            # Use database-specific upsert
            if IS_SQLITE:
                # SQLite: INSERT OR REPLACE
                stmt = sqlite_insert(PerformanceData).values(**record_data)
                stmt = stmt.on_conflict_do_update(
                    index_elements=["keyword_id", "profile_id", "date"],
                    set_={
                        "keyword_text": stmt.excluded.keyword_text,
                        "match_type": stmt.excluded.match_type,
                        "campaign_id": stmt.excluded.campaign_id,
                        "campaign_name": stmt.excluded.campaign_name,
                        "ad_group_id": stmt.excluded.ad_group_id,
                        "ad_group_name": stmt.excluded.ad_group_name,
                        "state": stmt.excluded.state,
                        "bid": stmt.excluded.bid,
                        "impressions": stmt.excluded.impressions,
                        "clicks": stmt.excluded.clicks,
                        "spend": stmt.excluded.spend,
                        "sales": stmt.excluded.sales,
                        "orders": stmt.excluded.orders,
                        "units_sold": stmt.excluded.units_sold,
                        "updated_at": datetime.utcnow(),
                    }
                )
            else:
                # PostgreSQL: INSERT ... ON CONFLICT ... DO UPDATE
                stmt = pg_insert(PerformanceData).values(**record_data)
                stmt = stmt.on_conflict_do_update(
                    index_elements=["keyword_id", "profile_id", "date"],
                    set_={
                        "keyword_text": stmt.excluded.keyword_text,
                        "match_type": stmt.excluded.match_type,
                        "campaign_id": stmt.excluded.campaign_id,
                        "campaign_name": stmt.excluded.campaign_name,
                        "ad_group_id": stmt.excluded.ad_group_id,
                        "ad_group_name": stmt.excluded.ad_group_name,
                        "state": stmt.excluded.state,
                        "bid": stmt.excluded.bid,
                        "impressions": stmt.excluded.impressions,
                        "clicks": stmt.excluded.clicks,
                        "spend": stmt.excluded.spend,
                        "sales": stmt.excluded.sales,
                        "orders": stmt.excluded.orders,
                        "units_sold": stmt.excluded.units_sold,
                        "updated_at": datetime.utcnow(),
                    }
                )

            session.execute(stmt)
            rows_added += 1

        session.commit()
        db_type = "SQLite" if IS_SQLITE else "PostgreSQL"
        logger.info(f"Successfully stored {rows_added} records in {db_type}")
        return rows_added

    except Exception as e:
        session.rollback()
        logger.error(f"Error storing performance records: {e}", exc_info=True)
        raise
    finally:
        session.close()


def query_performance(
    profile_id: str,
    start_date: date,
    end_date: date,
    campaign_id: Optional[str] = None,
    ad_group_id: Optional[str] = None,
    match_type: Optional[str] = None,
    keyword_state: Optional[str] = None,
) -> List[dict]:
    """Query performance data with filters from PostgreSQL.

    Args:
        profile_id: Amazon Ads profile ID
        start_date: Start date for query
        end_date: End date for query
        campaign_id: Optional campaign filter
        ad_group_id: Optional ad group filter
        match_type: Optional match type filter (exact, phrase, broad)
        keyword_state: Optional keyword state filter (enabled, paused, archived)

    Returns:
        List of performance records as dictionaries
    """
    logger.info(
        f"Querying performance data for profile {profile_id} "
        f"from {start_date} to {end_date}"
    )

    session = get_sync_session()
    try:
        # Build query with filters
        query = select(PerformanceData).where(
            and_(
                PerformanceData.profile_id == profile_id,
                PerformanceData.date >= start_date,
                PerformanceData.date <= end_date,
            )
        )

        if campaign_id:
            query = query.where(PerformanceData.campaign_id == campaign_id)
        if ad_group_id:
            query = query.where(PerformanceData.ad_group_id == ad_group_id)
        if match_type:
            query = query.where(PerformanceData.match_type == match_type)
        if keyword_state:
            query = query.where(PerformanceData.state == keyword_state)

        results = session.execute(query).scalars().all()

        # Convert to dictionaries
        records = []
        for record in results:
            records.append({
                "keyword_id": record.keyword_id,
                "keyword_text": record.keyword_text,
                "match_type": record.match_type,
                "campaign_id": record.campaign_id,
                "campaign_name": record.campaign_name,
                "ad_group_id": record.ad_group_id,
                "ad_group_name": record.ad_group_name,
                "state": record.state,
                "bid": record.bid,
                "date": record.date,
                "impressions": record.impressions,
                "clicks": record.clicks,
                "spend": record.spend,
                "sales": record.sales,
                "orders": record.orders,
                "units_sold": record.units_sold,
                "source": record.source,
                "created_at": record.created_at,
            })

        logger.info(f"Found {len(records)} records in date range")
        return records

    except Exception as e:
        logger.error(f"Error querying performance data: {e}", exc_info=True)
        raise
    finally:
        session.close()


def get_performance_summary(
    profile_id: str,
    start_date: date,
    end_date: date,
) -> dict:
    """Get aggregated performance summary from PostgreSQL.

    Args:
        profile_id: Amazon Ads profile ID
        start_date: Start date for summary
        end_date: End date for summary

    Returns:
        Dictionary with aggregated metrics
    """
    session = get_sync_session()
    try:
        # Use SQLAlchemy aggregation
        query = select(
            func.sum(PerformanceData.spend).label("total_spend"),
            func.sum(PerformanceData.sales).label("total_sales"),
            func.sum(PerformanceData.orders).label("total_orders"),
            func.sum(PerformanceData.impressions).label("total_impressions"),
            func.sum(PerformanceData.clicks).label("total_clicks"),
            func.count(func.distinct(PerformanceData.keyword_id)).label("keyword_count"),
        ).where(
            and_(
                PerformanceData.profile_id == profile_id,
                PerformanceData.date >= start_date,
                PerformanceData.date <= end_date,
            )
        )

        result = session.execute(query).one()

        total_spend = Decimal(str(result.total_spend)) if result.total_spend else Decimal("0")
        total_sales = Decimal(str(result.total_sales)) if result.total_sales else Decimal("0")
        total_orders = result.total_orders or 0
        total_impressions = result.total_impressions or 0
        total_clicks = result.total_clicks or 0
        keyword_count = result.keyword_count or 0

        # Calculate averages
        avg_acos = (total_spend / total_sales * 100) if total_sales > 0 else None
        avg_roas = (total_sales / total_spend) if total_spend > 0 else None
        avg_ctr = (Decimal(total_clicks) / Decimal(total_impressions) * 100) if total_impressions > 0 else None

        return {
            "total_spend": total_spend,
            "total_sales": total_sales,
            "total_orders": total_orders,
            "total_impressions": total_impressions,
            "total_clicks": total_clicks,
            "avg_acos": round(avg_acos, 2) if avg_acos else None,
            "avg_roas": round(avg_roas, 2) if avg_roas else None,
            "avg_ctr": round(avg_ctr, 2) if avg_ctr else None,
            "keyword_count": keyword_count,
        }

    except Exception as e:
        logger.error(f"Error getting performance summary: {e}", exc_info=True)
        raise
    finally:
        session.close()


def query_keywords(
    profile_id: str,
    start_date: date,
    end_date: date,
    page: int = 1,
    page_size: int = 50,
    sort_by: str = "spend",
    sort_order: str = "desc",
) -> tuple[List[dict], int]:
    """Query keyword-level performance with pagination and sorting from PostgreSQL.

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
    session = get_sync_session()
    try:
        # Aggregate by keyword_id
        query = select(
            PerformanceData.keyword_id,
            PerformanceData.keyword_text,
            PerformanceData.match_type,
            PerformanceData.campaign_name,
            PerformanceData.ad_group_name,
            PerformanceData.state,
            PerformanceData.bid,
            func.sum(PerformanceData.impressions).label("impressions"),
            func.sum(PerformanceData.clicks).label("clicks"),
            func.sum(PerformanceData.spend).label("spend"),
            func.sum(PerformanceData.sales).label("sales"),
            func.sum(PerformanceData.orders).label("orders"),
        ).where(
            and_(
                PerformanceData.profile_id == profile_id,
                PerformanceData.date >= start_date,
                PerformanceData.date <= end_date,
            )
        ).group_by(
            PerformanceData.keyword_id,
            PerformanceData.keyword_text,
            PerformanceData.match_type,
            PerformanceData.campaign_name,
            PerformanceData.ad_group_name,
            PerformanceData.state,
            PerformanceData.bid,
        )

        # Get total count before pagination
        count_query = select(func.count()).select_from(query.subquery())
        total_count = session.execute(count_query).scalar() or 0

        # Sort
        sort_field = getattr(PerformanceData, sort_by, PerformanceData.spend)
        if sort_order == "desc":
            query = query.order_by(sort_field.desc())
        else:
            query = query.order_by(sort_field.asc())

        # Paginate
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        results = session.execute(query).all()

        # Convert to dictionaries and calculate metrics
        keywords = []
        for row in results:
            spend = Decimal(str(row.spend)) if row.spend else Decimal("0")
            sales = Decimal(str(row.sales)) if row.sales else Decimal("0")
            clicks = row.clicks or 0
            impressions = row.impressions or 0

            kw = {
                "keyword_id": row.keyword_id,
                "keyword_text": row.keyword_text,
                "match_type": row.match_type,
                "campaign_name": row.campaign_name or "Unknown Campaign",
                "ad_group_name": row.ad_group_name or "Unknown Ad Group",
                "state": row.state,
                "bid": row.bid,
                "impressions": impressions,
                "clicks": clicks,
                "spend": spend,
                "sales": sales,
                "orders": row.orders or 0,
                "cpc": (spend / Decimal(clicks)) if clicks > 0 else None,
                "ctr": (Decimal(clicks) / Decimal(impressions) * 100) if impressions > 0 else None,
                "acos": (spend / sales * 100) if sales > 0 else None,
                "roas": (sales / spend) if spend > 0 else None,
                "conversion_rate": (Decimal(row.orders) / Decimal(clicks) * 100) if clicks > 0 else None,
            }
            keywords.append(kw)

        return keywords, total_count

    except Exception as e:
        logger.error(f"Error querying keywords: {e}", exc_info=True)
        raise
    finally:
        session.close()


def query_trends(
    profile_id: str,
    start_date: date,
    end_date: date,
    group_by: str = "day",
) -> List[dict]:
    """Query trend data grouped by time period from PostgreSQL.

    Args:
        profile_id: Amazon Ads profile ID
        start_date: Start date for trends
        end_date: End date for trends
        group_by: Grouping period (day, week, month)

    Returns:
        List of trend data points
    """
    session = get_sync_session()
    try:
        # Build query with date grouping
        date_field = PerformanceData.date

        if group_by == "week":
            # Group by week (Monday as start)
            date_field = func.date_trunc("week", PerformanceData.date)
        elif group_by == "month":
            # Group by month
            date_field = func.date_trunc("month", PerformanceData.date)

        query = select(
            date_field.label("date"),
            func.sum(PerformanceData.impressions).label("impressions"),
            func.sum(PerformanceData.clicks).label("clicks"),
            func.sum(PerformanceData.spend).label("spend"),
            func.sum(PerformanceData.sales).label("sales"),
            func.sum(PerformanceData.orders).label("orders"),
        ).where(
            and_(
                PerformanceData.profile_id == profile_id,
                PerformanceData.date >= start_date,
                PerformanceData.date <= end_date,
            )
        ).group_by(
            "date"
        ).order_by(
            "date"
        )

        results = session.execute(query).all()

        # Convert to dictionaries and calculate metrics
        trends = []
        for row in results:
            spend = Decimal(str(row.spend)) if row.spend else Decimal("0")
            sales = Decimal(str(row.sales)) if row.sales else Decimal("0")
            clicks = row.clicks or 0
            impressions = row.impressions or 0

            trend = {
                "date": row.date,
                "impressions": impressions,
                "clicks": clicks,
                "spend": spend,
                "sales": sales,
                "orders": row.orders or 0,
                "acos": (spend / sales * 100) if sales > 0 else None,
                "roas": (sales / spend) if spend > 0 else None,
                "ctr": (Decimal(clicks) / Decimal(impressions) * 100) if impressions > 0 else None,
            }
            trends.append(trend)

        return trends

    except Exception as e:
        logger.error(f"Error querying trends: {e}", exc_info=True)
        raise
    finally:
        session.close()


def get_data_sources(
    profile_id: str,
    start_date: date,
    end_date: date,
) -> dict:
    """Get information about data sources by date range from PostgreSQL.

    Args:
        profile_id: Amazon Ads profile ID
        start_date: Start date for query
        end_date: End date for query

    Returns:
        Dictionary with data source information
    """
    session = get_sync_session()
    try:
        # Count records by source
        query = select(
            PerformanceData.source,
            func.count(PerformanceData.id).label("record_count"),
        ).where(
            and_(
                PerformanceData.profile_id == profile_id,
                PerformanceData.date >= start_date,
                PerformanceData.date <= end_date,
            )
        ).group_by(
            PerformanceData.source
        )

        results = session.execute(query).all()

        sources = []
        total_records = 0
        api_records = 0
        upload_records = 0

        for row in results:
            source_info = {
                "start_date": start_date,
                "end_date": end_date,
                "source": row.source,
                "record_count": row.record_count,
            }
            sources.append(source_info)
            total_records += row.record_count

            if row.source == "api":
                api_records += row.record_count
            elif row.source == "upload":
                upload_records += row.record_count

        return {
            "profile_id": profile_id,
            "sources": sources,
            "total_records": total_records,
            "api_records": api_records,
            "upload_records": upload_records,
            "date_range_start": start_date,
            "date_range_end": end_date,
        }

    except Exception as e:
        logger.error(f"Error getting data sources: {e}", exc_info=True)
        raise
    finally:
        session.close()
