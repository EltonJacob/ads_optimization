"""SQLAlchemy database models for Amazon PPC data."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    DECIMAL,
    BigInteger,
    Date,
    DateTime,
    Integer,
    String,
    Text,
    Index,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


class PerformanceData(Base):
    """Keyword performance data from Amazon Ads."""

    __tablename__ = "performance_data"

    # Primary key
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # Amazon identifiers
    keyword_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    keyword_text: Mapped[str] = mapped_column(String(500), nullable=False)
    match_type: Mapped[str] = mapped_column(String(20), nullable=False)  # EXACT, PHRASE, BROAD

    campaign_id: Mapped[str] = mapped_column(String(100), nullable=True, index=True)
    campaign_name: Mapped[str] = mapped_column(String(500), nullable=True)

    ad_group_id: Mapped[str] = mapped_column(String(100), nullable=True)
    ad_group_name: Mapped[str] = mapped_column(String(500), nullable=True)

    profile_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # Status
    state: Mapped[str] = mapped_column(String(20), nullable=True)  # enabled, paused, archived
    bid: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(10, 2), nullable=True)

    # Date
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    # Performance metrics
    impressions: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    clicks: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    spend: Mapped[Decimal] = mapped_column(DECIMAL(12, 2), nullable=False, default=0)
    sales: Mapped[Decimal] = mapped_column(DECIMAL(12, 2), nullable=False, default=0)
    orders: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    units_sold: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Data source tracking
    source: Mapped[str] = mapped_column(String(20), nullable=False, default="api")  # 'api' or 'upload'

    # Indexes for query performance
    __table_args__ = (
        Index("idx_keyword_date", "keyword_id", "date"),
        Index("idx_profile_date", "profile_id", "date"),
        Index("idx_campaign_date", "campaign_id", "date"),
        Index("idx_date_range", "date", "profile_id"),
        # Unique constraint for upsert operations
        Index("idx_unique_keyword_profile_date", "keyword_id", "profile_id", "date", unique=True),
    )

    def __repr__(self) -> str:
        return f"<PerformanceData(keyword='{self.keyword_text}', date='{self.date}', spend={self.spend})>"


class ImportJob(Base):
    """Track import jobs from file uploads or API fetches."""

    __tablename__ = "import_jobs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    job_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    job_type: Mapped[str] = mapped_column(String(20), nullable=False)  # 'import' or 'fetch'

    profile_id: Mapped[str] = mapped_column(String(100), nullable=False)

    # Job status
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")  # pending, in_progress, completed, failed
    progress: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(5, 2), nullable=True)

    # Results
    rows_processed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    rows_added: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    rows_skipped: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    records_fetched: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Error tracking
    errors: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Timestamps
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    # Additional info (renamed from 'metadata' to avoid SQLAlchemy conflict)
    job_metadata: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string

    def __repr__(self) -> str:
        return f"<ImportJob(job_id='{self.job_id}', status='{self.status}', progress={self.progress})>"
