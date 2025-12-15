#!/usr/bin/env python3
"""
Environment Configuration Verification Script

Run this script to verify your .env file is properly configured.

Usage:
    python verify_env.py
"""

import os
import sys
from pathlib import Path

# Color codes for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def print_header(text: str) -> None:
    """Print a formatted header."""
    print(f"\n{BLUE}{'=' * 80}{RESET}")
    print(f"{BLUE}{text.center(80)}{RESET}")
    print(f"{BLUE}{'=' * 80}{RESET}\n")


def print_success(text: str) -> None:
    """Print success message."""
    print(f"{GREEN}✓ {text}{RESET}")


def print_error(text: str) -> None:
    """Print error message."""
    print(f"{RED}✗ {text}{RESET}")


def print_warning(text: str) -> None:
    """Print warning message."""
    print(f"{YELLOW}⚠ {text}{RESET}")


def print_info(text: str) -> None:
    """Print info message."""
    print(f"{BLUE}ℹ {text}{RESET}")


def check_env_file() -> bool:
    """Check if .env file exists."""
    env_path = Path(".env")
    if env_path.exists():
        print_success(f".env file found at: {env_path.resolve()}")
        return True
    else:
        print_error(".env file not found!")
        print_info("Run: cp .env.example .env")
        return False


def check_required_vars() -> dict:
    """Check for required environment variables."""
    # Load .env file
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print_success("python-dotenv loaded successfully")
    except ImportError:
        print_error("python-dotenv not installed!")
        print_info("Run: pip install python-dotenv")
        return {}

    results = {}

    # Database
    print_header("DATABASE CONFIGURATION")
    db_url = os.getenv("DATABASE_URL")
    if db_url and db_url != "sqlite:///amazon_ppc.db":
        if db_url.startswith("postgresql"):
            print_success(f"PostgreSQL configured: {db_url.split('@')[-1] if '@' in db_url else 'local'}")
        elif db_url.startswith("sqlite"):
            print_success("SQLite configured (development mode)")
        results["database"] = True
    elif db_url == "sqlite:///amazon_ppc.db":
        print_warning("Using default SQLite configuration")
        print_info("For production, consider PostgreSQL")
        results["database"] = True
    else:
        print_error("DATABASE_URL not set")
        results["database"] = False

    # Amazon Ads API
    print_header("AMAZON ADS API CREDENTIALS")
    amazon_vars = {
        "AMAZON_ADS_CLIENT_ID": "Client ID",
        "AMAZON_ADS_CLIENT_SECRET": "Client Secret",
        "AMAZON_ADS_REFRESH_TOKEN": "Refresh Token",
    }

    amazon_configured = True
    for var, name in amazon_vars.items():
        value = os.getenv(var)
        if value and value != "" and not value.startswith("your_"):
            print_success(f"{name}: {value[:10]}{'*' * (len(value) - 10)}")
        else:
            print_error(f"{name} not configured")
            amazon_configured = False

    results["amazon_api"] = amazon_configured

    if not amazon_configured:
        print_info("Get credentials from: https://advertising.amazon.com/API/docs/en-us/get-started/overview")

    # AI Provider
    print_header("AI PROVIDER CONFIGURATION")
    ai_provider = os.getenv("AI_PROVIDER", "").lower()
    openai_key = os.getenv("OPENAI_API_KEY", "")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")

    ai_configured = False

    if ai_provider == "openai":
        if openai_key and not openai_key.startswith("your_"):
            print_success(f"OpenAI configured: {openai_key[:10]}{'*' * 20}")
            ai_model = os.getenv("AI_MODEL", "gpt-4-turbo-preview")
            print_info(f"Using model: {ai_model}")
            ai_configured = True
        else:
            print_error("AI_PROVIDER set to 'openai' but OPENAI_API_KEY not configured")
            print_info("Get API key from: https://platform.openai.com/api-keys")
    elif ai_provider == "anthropic":
        if anthropic_key and not anthropic_key.startswith("your_"):
            print_success(f"Anthropic configured: {anthropic_key[:10]}{'*' * 20}")
            ai_model = os.getenv("AI_MODEL", "claude-3-opus-20240229")
            print_info(f"Using model: {ai_model}")
            ai_configured = True
        else:
            print_error("AI_PROVIDER set to 'anthropic' but ANTHROPIC_API_KEY not configured")
            print_info("Get API key from: https://console.anthropic.com/")
    else:
        print_warning(f"AI_PROVIDER not set or invalid: '{ai_provider}'")
        print_info("Set AI_PROVIDER to 'openai' or 'anthropic'")

        # Check if any key is set
        if openai_key and not openai_key.startswith("your_"):
            print_info("OpenAI API key detected - set AI_PROVIDER=openai")
        if anthropic_key and not anthropic_key.startswith("your_"):
            print_info("Anthropic API key detected - set AI_PROVIDER=anthropic")

    results["ai_provider"] = ai_configured

    # Optimization Parameters
    print_header("OPTIMIZATION PARAMETERS")
    opt_params = {
        "TARGET_ACOS": ("Target ACOS", "0.25"),
        "MIN_BID": ("Minimum Bid", "0.20"),
        "MAX_BID": ("Maximum Bid", "1.60"),
        "OPTIMIZE_DEFAULT_MODE": ("Default Mode", "dry-run"),
    }

    for var, (name, default) in opt_params.items():
        value = os.getenv(var, default)
        print_success(f"{name}: {value}")

    results["optimization"] = True

    # Application Settings
    print_header("APPLICATION SETTINGS")
    api_host = os.getenv("API_HOST", "0.0.0.0")
    api_port = os.getenv("API_PORT", "8000")
    debug = os.getenv("DEBUG", "True")
    log_level = os.getenv("LOG_LEVEL", "INFO")

    print_success(f"API Server: {api_host}:{api_port}")
    print_success(f"Debug Mode: {debug}")
    print_success(f"Log Level: {log_level}")

    if debug.lower() == "true":
        print_warning("Debug mode enabled - disable in production!")

    results["application"] = True

    return results


def check_dependencies() -> bool:
    """Check if required Python packages are installed."""
    print_header("PYTHON DEPENDENCIES")

    required_packages = [
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "pydantic",
        "dotenv",
        "httpx",
    ]

    all_installed = True
    for package in required_packages:
        try:
            if package == "dotenv":
                __import__("dotenv")
            else:
                __import__(package)
            print_success(f"{package} installed")
        except ImportError:
            print_error(f"{package} not installed")
            all_installed = False

    if not all_installed:
        print_info("Run: pip install -r requirements.txt")

    return all_installed


def main():
    """Main verification function."""
    print_header("AMAZON PPC OPTIMIZATION TOOL - ENVIRONMENT VERIFICATION")

    # Check .env file exists
    if not check_env_file():
        sys.exit(1)

    # Check dependencies
    deps_ok = check_dependencies()

    # Check environment variables
    results = check_required_vars()

    # Summary
    print_header("VERIFICATION SUMMARY")

    all_good = True

    if results.get("database"):
        print_success("Database configuration: OK")
    else:
        print_error("Database configuration: MISSING")
        all_good = False

    if results.get("amazon_api"):
        print_success("Amazon Ads API credentials: OK")
    else:
        print_error("Amazon Ads API credentials: MISSING")
        all_good = False

    if results.get("ai_provider"):
        print_success("AI Provider configuration: OK")
    else:
        print_error("AI Provider configuration: MISSING")
        all_good = False

    if deps_ok:
        print_success("Python dependencies: OK")
    else:
        print_error("Python dependencies: INCOMPLETE")
        all_good = False

    print()

    if all_good:
        print_success("All checks passed! Your environment is properly configured.")
        print_info("Next steps:")
        print("  1. Run database migrations (when ready)")
        print("  2. Start the API server: python -m agent api")
        print("  3. Visit API docs: http://localhost:8000/docs")
        return 0
    else:
        print_warning("Some configuration issues detected.")
        print_info("Please review the errors above and update your .env file.")
        print_info("See ENV_SETUP_GUIDE.md for detailed instructions.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
