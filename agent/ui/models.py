"""Pydantic models for API request/response validation."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


# ============================================================================
# Enums
# ============================================================================

class OptimizeMode(str, Enum):
    """Optimization execution mode."""
    DRY_RUN = "dry-run"
    APPLY = "apply"


class JobStatus(str, Enum):
    """Status of async jobs."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


class DataSource(str, Enum):
    """Source of performance data."""
    API = "api"
    UPLOAD = "upload"


# ============================================================================
# Base Response Models
# ============================================================================

class APIResponse(BaseModel):
    """Base API response."""
    success: bool
    message: str
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    """Error response."""
    success: bool = False
    error: str
    detail: Optional[str] = None


# ============================================================================
# Health & Status
# ============================================================================

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    service: str
    database: str


# ============================================================================
# Data Fetch Models
# ============================================================================

class FetchRequest(BaseModel):
    """Request to fetch data from Amazon Ads API."""
    profile_id: str = Field(..., description="Amazon Ads profile ID")
    start_date: date = Field(..., description="Start date for report (YYYY-MM-DD)")
    end_date: date = Field(..., description="End date for report (YYYY-MM-DD)")
    report_type: str = Field(default="KEYWORDS", description="Type of report to fetch")


class FetchResponse(BaseModel):
    """Response from fetch request."""
    job_id: str
    status: JobStatus
    message: str


class FetchStatusResponse(BaseModel):
    """Status of a fetch job."""
    job_id: str
    status: JobStatus
    progress: Optional[float] = Field(None, ge=0, le=100, description="Progress percentage")
    records_fetched: int = 0
    errors: list[str] = Field(default_factory=list)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


# ============================================================================
# Upload & Import Models
# ============================================================================

class UploadResponse(BaseModel):
    """Response from file upload."""
    upload_id: str
    filename: str
    file_type: str
    size_bytes: int
    upload_path: str
    uploaded_at: datetime
    message: str


class UploadValidationError(BaseModel):
    """File upload validation error."""
    field: str
    message: str


class FilePreviewRow(BaseModel):
    """Preview row from uploaded file."""
    row_number: int
    data: dict[str, Any]


class FilePreviewResponse(BaseModel):
    """Preview of uploaded file."""
    upload_id: str
    filename: str
    total_rows: int
    preview_rows: list[FilePreviewRow]
    detected_columns: list[str]
    missing_columns: list[str]
    validation_errors: list[UploadValidationError] = Field(default_factory=list)


class ImportRequest(BaseModel):
    """Request to import uploaded file."""
    upload_id: str
    profile_id: str
    start_date: Optional[date] = Field(
        None,
        description="Start date for date range filter (optional, uses dates from file if not provided)"
    )
    end_date: Optional[date] = Field(
        None,
        description="End date for date range filter (optional, uses dates from file if not provided)"
    )


class ImportResponse(BaseModel):
    """Response from import operation."""
    success: bool
    job_id: str
    rows_processed: int
    rows_added: int
    rows_skipped: int
    errors: list[str] = Field(default_factory=list)
    message: str


class ImportStatusResponse(BaseModel):
    """Status of an import job."""
    job_id: str
    status: JobStatus
    progress: Optional[float] = Field(None, ge=0, le=100, description="Progress percentage")
    rows_processed: int = 0
    rows_added: int = 0
    rows_skipped: int = 0
    errors: list[str] = Field(default_factory=list)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


# ============================================================================
# Performance Data Models
# ============================================================================

class KeywordPerformance(BaseModel):
    """Keyword performance metrics."""
    model_config = ConfigDict(from_attributes=True)

    keyword_id: int
    keyword_text: str
    match_type: str
    bid: Optional[Decimal]
    state: str
    impressions: int
    clicks: int
    spend: Decimal
    sales: Decimal
    orders: int
    cpc: Optional[Decimal]
    ctr: Optional[Decimal]
    acos: Optional[Decimal]
    roas: Optional[Decimal]


class PerformanceSummary(BaseModel):
    """Aggregated performance summary."""
    total_spend: Decimal
    total_sales: Decimal
    total_orders: int
    total_impressions: int
    total_clicks: int
    avg_acos: Optional[Decimal]
    avg_roas: Optional[Decimal]
    avg_ctr: Optional[Decimal]
    keyword_count: int


class PerformanceQueryParams(BaseModel):
    """Query parameters for performance data."""
    start_date: date
    end_date: date
    campaign_id: Optional[int] = None
    ad_group_id: Optional[int] = None
    match_type: Optional[str] = None
    keyword_state: Optional[str] = None
    group_by: Optional[str] = Field(default="day", pattern="^(day|week|month)$")


# ============================================================================
# Recommendation Models
# ============================================================================

class BidRecommendation(BaseModel):
    """Bid adjustment recommendation."""
    keyword_id: int
    keyword_text: str
    campaign_name: str
    current_bid: Decimal
    recommended_bid: Decimal
    adjustment_percentage: float
    reasoning: str
    confidence_score: float = Field(ge=0, le=100)
    expected_impact: str


class KeywordPauseRecommendation(BaseModel):
    """Keyword pause recommendation."""
    keyword_id: int
    keyword_text: str
    campaign_name: str
    spend: Decimal
    orders: int
    acos: Optional[Decimal]
    reasoning: str
    confidence_score: float = Field(ge=0, le=100)
    wasted_spend: Decimal


class KeywordEnableRecommendation(BaseModel):
    """Keyword enable recommendation."""
    keyword_id: int
    keyword_text: str
    campaign_name: str
    paused_date: Optional[date]
    reason_to_enable: str
    suggested_bid: Decimal
    confidence_score: float = Field(ge=0, le=100)


class RecommendationBatch(BaseModel):
    """Batch of recommendations."""
    batch_id: str
    generated_at: datetime
    start_date: date
    end_date: date
    bid_adjustments: list[BidRecommendation] = Field(default_factory=list)
    keywords_to_pause: list[KeywordPauseRecommendation] = Field(default_factory=list)
    keywords_to_enable: list[KeywordEnableRecommendation] = Field(default_factory=list)
    total_count: int


class GenerateRecommendationsRequest(BaseModel):
    """Request to generate recommendations."""
    profile_id: str
    start_date: date
    end_date: date
    target_acos: Optional[float] = None
    min_bid: Optional[float] = None
    max_bid: Optional[float] = None


class ApplyRecommendationRequest(BaseModel):
    """Request to apply recommendation(s)."""
    recommendation_ids: list[str]
    apply_immediately: bool = True


# ============================================================================
# Decision & Audit Models
# ============================================================================

class DecisionRecord(BaseModel):
    """Decision/change record."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    date: date
    keyword_id: Optional[int]
    action: str
    old_bid: Optional[Decimal]
    new_bid: Optional[Decimal]
    reason: Optional[str]
    policy_version: Optional[str]
    created_at: datetime


class DecisionHistoryResponse(BaseModel):
    """Decision history response."""
    decisions: list[DecisionRecord]
    total: int
    page: int
    page_size: int
