"""Simple CLI entrypoint for python -m agent."""

from __future__ import annotations

import argparse
from dataclasses import asdict

from agent.config import settings
from agent.context import generate_job_id
from agent.jobs import fetch_reports, fetch_reports_mock, healthcheck, import_spreadsheet, optimize
from agent.logging import setup_logging
from agent.ui import app as ui_app

CONFIG_SENSITIVE_KEYS = {
    "amazon_ads_client_id",
    "amazon_ads_client_secret",
    "amazon_ads_refresh_token",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Amazon PPC agent scaffold.")
    sub = parser.add_subparsers(dest="command")

    reports = sub.add_parser("fetch", help="Fetch performance reports.")
    reports.add_argument("--days", type=int, default=30)

    mock_reports = sub.add_parser("fetch-mock", help="Generate mock performance data (for testing).")
    mock_reports.add_argument("--days", type=int, default=30)

    import_cmd = sub.add_parser("import", help="Import keyword performance data from CSV/Excel file.")
    import_cmd.add_argument("file", help="Path to CSV or Excel file")

    opt = sub.add_parser("optimize", help="Run optimization loop.")
    opt.add_argument("--window", type=int, default=settings.optimize_default_window)
    opt.add_argument(
        "--mode",
        choices=["dry-run", "apply"],
        default=settings.optimize_default_mode,
    )

    sub.add_parser("healthcheck", help="Call Amazon Ads API and list profiles.")
    sub.add_parser("ui", help="Launch placeholder UI.")

    api = sub.add_parser("api", help="Launch FastAPI server.")
    api.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind to")
    api.add_argument("--port", type=int, default=8000, help="Port to bind to")
    api.add_argument("--reload", action="store_true", help="Enable auto-reload (development)")

    sub.add_parser("config", help="Print effective configuration (secrets redacted).")
    return parser


def print_config() -> None:
    """Display configuration with secrets hidden."""
    data = asdict(settings)
    for key in data:
        if key in CONFIG_SENSITIVE_KEYS and data[key]:
            data[key] = "***redacted***"
    for key in sorted(data):
        print(f"{key}={data[key]}")


def launch_api(host: str = "0.0.0.0", port: int = 8000, reload: bool = False) -> None:
    """Launch the FastAPI server."""
    import uvicorn

    print(f"🚀 Starting Amazon PPC API server on http://{host}:{port}")
    print(f"📚 API documentation available at http://{host}:{port}/docs")
    print(f"🔄 Auto-reload: {'enabled' if reload else 'disabled'}")

    uvicorn.run(
        "agent.ui.api:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info",
    )


def main() -> None:
    setup_logging(settings.log_level, service="amazon-ppc-agent")
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "fetch":
        job_id = generate_job_id("fetch")
        fetch_reports.run(days=args.days, job_id=job_id)
    elif args.command == "fetch-mock":
        job_id = generate_job_id("fetch-mock")
        fetch_reports_mock.run(days=args.days, job_id=job_id)
    elif args.command == "import":
        job_id = generate_job_id("import")
        import_spreadsheet.run(file_path=args.file, job_id=job_id)
    elif args.command == "optimize":
        job_id = generate_job_id("optimize")
        optimize.run(window=args.window, mode=args.mode, job_id=job_id)
    elif args.command == "healthcheck":
        profiles = healthcheck.run()
        healthcheck.print_profiles(profiles)
    elif args.command == "ui":
        ui_app.main()
    elif args.command == "api":
        launch_api(host=args.host, port=args.port, reload=args.reload)
    elif args.command == "config":
        print_config()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
