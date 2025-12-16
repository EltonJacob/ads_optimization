"""FastAPI application with CORS middleware for frontend integration."""

from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import date, datetime
from pathlib import Path
from typing import AsyncGenerator

from fastapi import BackgroundTasks, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from agent.config import settings
from agent.context import generate_job_id
from agent.jobs import fetch_reports, import_spreadsheet
from agent.jobs.job_tracker import JobStatus, get_tracker
from agent.ui import file_utils
from agent.ui.models import (
    DataSourceResponse,
    FetchRequest,
    FetchResponse,
    FetchStatusResponse,
    FilePreviewResponse,
    FilePreviewRow,
    ImportRequest,
    ImportResponse,
    ImportStatusResponse,
    KeywordListResponse,
    PerformanceSummary,
    TrendResponse,
    UploadResponse,
    UploadValidationError,
)

logger = logging.getLogger(__name__)


async def import_spreadsheet_async(job_id: str, file_path: str, profile_id: str) -> None:
    """Import spreadsheet file as a background job.

    Args:
        job_id: Unique job identifier for tracking
        file_path: Path to the uploaded file
        profile_id: Amazon Ads profile ID
    """
    tracker = get_tracker()

    try:
        # Update job status to in_progress
        await tracker.update_job(job_id, status=JobStatus.IN_PROGRESS, progress=10.0)

        # Run the import synchronously (import_spreadsheet.run is not async)
        logger.info(f"Starting import for job {job_id}: {file_path}")

        # Import the file
        records = []
        file_path_obj = Path(file_path)
        suffix = file_path_obj.suffix.lower()

        if suffix == ".csv":
            records = import_spreadsheet.import_csv(file_path_obj)
        elif suffix in (".xlsx", ".xls"):
            records = import_spreadsheet.import_excel(file_path_obj)
        else:
            raise ValueError(f"Unsupported file type: {suffix}")

        await tracker.update_job(job_id, progress=50.0)

        if not records:
            await tracker.update_job(
                job_id,
                status=JobStatus.COMPLETED,
                progress=100.0,
                error="No valid records found in file"
            )
            return

        # Persist to database
        from agent.data import dao
        persisted = dao.upsert_performance(records)

        # Update job status with results
        job = await tracker.get_job(job_id)
        if job and job.metadata:
            job.metadata["rows_processed"] = len(records)
            job.metadata["rows_added"] = persisted
            job.metadata["rows_skipped"] = len(records) - persisted

        await tracker.update_job(
            job_id,
            status=JobStatus.COMPLETED,
            progress=100.0,
            records_fetched=persisted
        )

        logger.info(
            f"Import job {job_id} completed: {len(records)} records processed, "
            f"{persisted} persisted to database"
        )

    except Exception as exc:
        logger.error(f"Import job {job_id} failed: {exc}", exc_info=True)
        await tracker.update_job(
            job_id,
            status=JobStatus.FAILED,
            error=str(exc)
        )


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application lifecycle events."""
    logger.info("FastAPI application starting up")
    yield
    logger.info("FastAPI application shutting down")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Amazon PPC Optimization API",
        description="AI-powered Amazon PPC campaign optimization and bid management",
        version="1.0.0",
        lifespan=lifespan,
    )

    # Configure CORS middleware for frontend integration
    # This allows the frontend (running on a different port) to make API requests
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",      # Next.js default dev server
            "http://localhost:3001",      # Alternative frontend port
            "http://127.0.0.1:3000",      # Alternative localhost
            "http://127.0.0.1:3001",
        ],
        allow_credentials=True,           # Allow cookies and authorization headers
        allow_methods=["*"],              # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
        allow_headers=["*"],              # Allow all headers
    )

    # Register API routes
    register_routes(app)

    return app


def register_routes(app: FastAPI) -> None:
    """Register all API route handlers."""

    @app.get("/")
    async def root():
        """Root endpoint - API health check."""
        return {
            "message": "Amazon PPC Optimization API",
            "version": "1.0.0",
            "status": "running"
        }

    @app.get("/api/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "service": "amazon-ppc-api",
            "database": settings.database_url.split("://")[0],  # Show db type without credentials
        }

    @app.post("/api/fetch", response_model=FetchResponse)
    async def trigger_fetch(request: FetchRequest, background_tasks: BackgroundTasks):
        """Trigger Amazon Ads API fetch for performance data.

        This endpoint starts an async job to fetch performance data from Amazon Ads API.
        The job runs in the background and can be monitored via the status endpoint.

        Args:
            request: FetchRequest with profile_id, start_date, end_date, report_type
            background_tasks: FastAPI background task manager

        Returns:
            FetchResponse with job_id and initial status
        """
        # Generate unique job ID
        job_id = generate_job_id("fetch")

        # Create job entry in tracker
        tracker = get_tracker()
        await tracker.create_job(
            job_id=job_id,
            job_type="fetch",
            metadata={
                "profile_id": request.profile_id,
                "start_date": str(request.start_date),
                "end_date": str(request.end_date),
                "report_type": request.report_type,
            }
        )

        # Start the fetch job in the background
        background_tasks.add_task(
            fetch_reports.fetch_reports_async,
            job_id=job_id,
            profile_id=request.profile_id,
            start_date=request.start_date,
            end_date=request.end_date,
            report_type=request.report_type,
        )

        logger.info(
            f"Started fetch job {job_id} for profile {request.profile_id} "
            f"from {request.start_date} to {request.end_date}"
        )

        return FetchResponse(
            job_id=job_id,
            status=JobStatus.PENDING,
            message=f"Fetch job started. Monitor progress at /api/fetch/status/{job_id}"
        )

    @app.get("/api/fetch/status/{job_id}", response_model=FetchStatusResponse)
    async def get_fetch_status(job_id: str):
        """Get the status of a fetch job.

        Args:
            job_id: The unique job identifier returned from POST /api/fetch

        Returns:
            FetchStatusResponse with current job status and progress

        Raises:
            HTTPException: 404 if job_id not found
        """
        tracker = get_tracker()
        job = await tracker.get_job(job_id)

        if not job:
            raise HTTPException(
                status_code=404,
                detail=f"Job {job_id} not found"
            )

        return FetchStatusResponse(
            job_id=job.job_id,
            status=job.status,
            progress=job.progress,
            records_fetched=job.records_fetched,
            errors=job.errors,
            started_at=job.started_at,
            completed_at=job.completed_at,
        )

    # ========================================================================
    # UPLOAD & IMPORT ENDPOINTS
    # ========================================================================

    @app.post("/api/upload", response_model=UploadResponse)
    async def upload_file(
        file: UploadFile = File(..., description="CSV or Excel file to upload"),
        profile_id: str = Form(..., description="Amazon Ads profile ID"),
    ):
        """Upload a spreadsheet file for import.

        This endpoint accepts CSV or Excel files containing keyword performance data.
        The file is validated and stored for later import.

        Args:
            file: The uploaded file (CSV or Excel)
            profile_id: Amazon Ads profile ID for organizing uploads

        Returns:
            UploadResponse with upload_id and file metadata

        Raises:
            HTTPException: 400 if validation fails
        """
        # Validate file type
        is_valid, error_msg = file_utils.validate_file_type(file.filename or "")
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)

        # Read file to check size
        content = await file.read()
        file_size = len(content)

        # Validate file size
        is_valid, error_msg = file_utils.validate_file_size(file_size)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)

        # Reset file pointer for saving
        await file.seek(0)

        # Generate upload ID and get storage path
        upload_id = file_utils.generate_upload_id()
        upload_path = file_utils.get_upload_path(upload_id, file.filename or "file", profile_id)

        # Save file
        bytes_written = await file_utils.save_upload_file(file, upload_path)

        logger.info(
            f"File uploaded: {upload_id} - {file.filename} ({bytes_written} bytes) "
            f"for profile {profile_id}"
        )

        return UploadResponse(
            upload_id=upload_id,
            filename=file.filename or "unknown",
            file_type=upload_path.suffix,
            size_bytes=bytes_written,
            upload_path=str(upload_path),
            uploaded_at=datetime.now(),
            message=f"File uploaded successfully. Use upload_id '{upload_id}' to import."
        )

    @app.get("/api/upload/{upload_id}/preview", response_model=FilePreviewResponse)
    async def preview_upload(upload_id: str):
        """Preview uploaded file contents and validate columns.

        This endpoint returns a preview of the first 10 rows and validates
        that all required columns are present.

        Args:
            upload_id: The upload identifier from POST /api/upload

        Returns:
            FilePreviewResponse with preview rows and validation results

        Raises:
            HTTPException: 404 if file not found
        """
        # Find the uploaded file
        upload_dir = Path("data/uploads")
        uploaded_files = list(upload_dir.rglob(f"{upload_id}.*"))

        if not uploaded_files:
            raise HTTPException(
                status_code=404,
                detail=f"Upload {upload_id} not found"
            )

        file_path = uploaded_files[0]

        # Validate columns
        file_ext = file_path.suffix.lower()
        if file_ext == ".csv":
            detected_columns, missing_columns = file_utils.validate_csv_columns(file_path)
        elif file_ext in (".xlsx", ".xls"):
            detected_columns, missing_columns = file_utils.validate_excel_columns(file_path)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file_ext}"
            )

        # Get file preview
        preview_data, total_rows = file_utils.get_file_preview(file_path, max_rows=10)

        # Convert to preview rows
        preview_rows = [
            FilePreviewRow(row_number=i + 1, data=row)
            for i, row in enumerate(preview_data)
        ]

        # Build validation errors
        validation_errors = []
        if missing_columns:
            validation_errors.append(
                UploadValidationError(
                    field="columns",
                    message=f"Missing required columns: {', '.join(missing_columns)}"
                )
            )

        return FilePreviewResponse(
            upload_id=upload_id,
            filename=file_path.name,
            total_rows=total_rows,
            preview_rows=preview_rows,
            detected_columns=detected_columns,
            missing_columns=missing_columns,
            validation_errors=validation_errors,
        )

    @app.post("/api/import", response_model=ImportResponse)
    async def import_file(request: ImportRequest, background_tasks: BackgroundTasks):
        """Import uploaded spreadsheet file into database.

        This endpoint processes an uploaded file and imports the keyword performance
        data into the database. The import runs as a background job.

        Args:
            request: ImportRequest with upload_id, profile_id, and optional date range
            background_tasks: FastAPI background task manager

        Returns:
            ImportResponse with job_id and initial status

        Raises:
            HTTPException: 404 if upload not found, 400 if validation fails
        """
        # Find the uploaded file
        upload_dir = Path("data/uploads")
        uploaded_files = list(upload_dir.rglob(f"{request.upload_id}.*"))

        if not uploaded_files:
            raise HTTPException(
                status_code=404,
                detail=f"Upload {request.upload_id} not found"
            )

        file_path = uploaded_files[0]

        # Validate columns before starting import
        file_ext = file_path.suffix.lower()
        if file_ext == ".csv":
            detected_columns, missing_columns = file_utils.validate_csv_columns(file_path)
        elif file_ext in (".xlsx", ".xls"):
            detected_columns, missing_columns = file_utils.validate_excel_columns(file_path)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file_ext}"
            )

        if missing_columns:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required columns: {', '.join(missing_columns)}. "
                       f"Please ensure your file has: {', '.join(file_utils.REQUIRED_COLUMNS)}"
            )

        # Generate job ID
        job_id = generate_job_id("import")

        # Create job entry in tracker
        tracker = get_tracker()
        await tracker.create_job(
            job_id=job_id,
            job_type="import",
            metadata={
                "upload_id": request.upload_id,
                "profile_id": request.profile_id,
                "file_path": str(file_path),
                "start_date": str(request.start_date) if request.start_date else None,
                "end_date": str(request.end_date) if request.end_date else None,
            }
        )

        # Start the import job in the background
        background_tasks.add_task(
            import_spreadsheet_async,
            job_id=job_id,
            file_path=str(file_path),
            profile_id=request.profile_id,
        )

        logger.info(
            f"Started import job {job_id} for upload {request.upload_id} "
            f"(profile: {request.profile_id})"
        )

        return ImportResponse(
            success=True,
            job_id=job_id,
            rows_processed=0,
            rows_added=0,
            rows_skipped=0,
            errors=[],
            message=f"Import job started. Monitor progress at /api/import/status/{job_id}"
        )

    @app.get("/api/import/status/{job_id}", response_model=ImportStatusResponse)
    async def get_import_status(job_id: str):
        """Get the status of an import job.

        Args:
            job_id: The unique job identifier returned from POST /api/import

        Returns:
            ImportStatusResponse with current job status and progress

        Raises:
            HTTPException: 404 if job_id not found
        """
        tracker = get_tracker()
        job = await tracker.get_job(job_id)

        if not job:
            raise HTTPException(
                status_code=404,
                detail=f"Job {job_id} not found"
            )

        return ImportStatusResponse(
            job_id=job.job_id,
            status=job.status,
            progress=job.progress,
            rows_processed=job.metadata.get("rows_processed", 0) if job.metadata else 0,
            rows_added=job.metadata.get("rows_added", 0) if job.metadata else 0,
            rows_skipped=job.metadata.get("rows_skipped", 0) if job.metadata else 0,
            errors=job.errors,
            started_at=job.started_at,
            completed_at=job.completed_at,
        )

    # ========================================================================
    # PERFORMANCE QUERY ENDPOINTS
    # ========================================================================

    @app.get("/api/performance/{profile_id}/summary", response_model=PerformanceSummary)
    async def get_performance_summary(
        profile_id: str,
        start_date: date,
        end_date: date,
    ):
        """Get aggregated performance summary for a profile.

        This endpoint returns overall performance metrics aggregated across
        all keywords for the specified date range.

        Args:
            profile_id: Amazon Ads profile ID
            start_date: Start date for query (YYYY-MM-DD)
            end_date: End date for query (YYYY-MM-DD)

        Returns:
            PerformanceSummary with aggregated metrics

        Example:
            GET /api/performance/profile_123/summary?start_date=2025-11-01&end_date=2025-11-30
        """
        from agent.data import dao

        summary = dao.get_performance_summary(profile_id, start_date, end_date)

        return PerformanceSummary(**summary)

    @app.get("/api/performance/{profile_id}/keywords", response_model=KeywordListResponse)
    async def get_keywords(
        profile_id: str,
        start_date: date,
        end_date: date,
        page: int = 1,
        page_size: int = 50,
        sort_by: str = "spend",
        sort_order: str = "desc",
    ):
        """Get keyword-level performance data with pagination and sorting.

        This endpoint returns performance data for individual keywords,
        with support for pagination and sorting.

        Args:
            profile_id: Amazon Ads profile ID
            start_date: Start date for query (YYYY-MM-DD)
            end_date: End date for query (YYYY-MM-DD)
            page: Page number (1-indexed, default: 1)
            page_size: Number of results per page (default: 50)
            sort_by: Field to sort by (spend, sales, clicks, impressions, acos)
            sort_order: Sort order (asc, desc)

        Returns:
            KeywordListResponse with paginated keyword data

        Example:
            GET /api/performance/profile_123/keywords?start_date=2025-11-01&end_date=2025-11-30&page=1&page_size=50&sort_by=spend&sort_order=desc
        """
        from agent.data import dao

        keywords, total_count = dao.query_keywords(
            profile_id=profile_id,
            start_date=start_date,
            end_date=end_date,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        return KeywordListResponse(
            profile_id=profile_id,
            keywords=keywords,
            total_count=total_count,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    @app.get("/api/performance/{profile_id}/trends", response_model=TrendResponse)
    async def get_trends(
        profile_id: str,
        start_date: date,
        end_date: date,
        group_by: str = "day",
    ):
        """Get performance trend data over time.

        This endpoint returns time-series performance data grouped by
        day, week, or month for charting and trend analysis.

        Args:
            profile_id: Amazon Ads profile ID
            start_date: Start date for trends (YYYY-MM-DD)
            end_date: End date for trends (YYYY-MM-DD)
            group_by: Grouping period (day, week, month)

        Returns:
            TrendResponse with time-series data points

        Example:
            GET /api/performance/profile_123/trends?start_date=2025-11-01&end_date=2025-11-30&group_by=day
        """
        from agent.data import dao

        if group_by not in ("day", "week", "month"):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid group_by value: {group_by}. Must be 'day', 'week', or 'month'"
            )

        trends = dao.query_trends(
            profile_id=profile_id,
            start_date=start_date,
            end_date=end_date,
            group_by=group_by,
        )

        return TrendResponse(
            profile_id=profile_id,
            start_date=start_date,
            end_date=end_date,
            group_by=group_by,
            data_points=trends,
        )

    @app.get("/api/performance/{profile_id}/sources", response_model=DataSourceResponse)
    async def get_data_sources(
        profile_id: str,
        start_date: date,
        end_date: date,
    ):
        """Get information about data sources for a date range.

        This endpoint shows which data came from the Amazon Ads API vs.
        uploaded spreadsheets, helping identify data gaps.

        Args:
            profile_id: Amazon Ads profile ID
            start_date: Start date for query (YYYY-MM-DD)
            end_date: End date for query (YYYY-MM-DD)

        Returns:
            DataSourceResponse with source breakdown

        Example:
            GET /api/performance/profile_123/sources?start_date=2025-11-01&end_date=2025-11-30
        """
        from agent.data import dao

        sources = dao.get_data_sources(
            profile_id=profile_id,
            start_date=start_date,
            end_date=end_date,
        )

        return DataSourceResponse(**sources)


# Create the app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn

    # Run the server
    uvicorn.run(
        "agent.ui.api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes (development only)
        log_level="info",
    )
