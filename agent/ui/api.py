"""FastAPI application with CORS middleware for frontend integration."""

from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from agent.config import settings
from agent.context import generate_job_id
from agent.jobs import fetch_reports
from agent.jobs.job_tracker import JobStatus, get_tracker
from agent.ui.models import FetchRequest, FetchResponse, FetchStatusResponse

logger = logging.getLogger(__name__)


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
