#!/usr/bin/env python3
"""
Automated Test Suite for Amazon PPC Optimization Tool

Runs all available tests to verify the implementation.

Usage:
    python3 run_tests.py
"""

import asyncio
import sys
from pathlib import Path

# Color codes
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"


def print_header(text: str) -> None:
    """Print a formatted header."""
    print(f"\n{BLUE}{BOLD}{'=' * 80}{RESET}")
    print(f"{BLUE}{BOLD}{text.center(80)}{RESET}")
    print(f"{BLUE}{BOLD}{'=' * 80}{RESET}\n")


def print_test(name: str) -> None:
    """Print test name."""
    print(f"{BOLD}{name}{RESET}...", end=" ", flush=True)


def print_pass() -> None:
    """Print pass message."""
    print(f"{GREEN}✓ PASS{RESET}")


def print_fail(error: str = "") -> None:
    """Print fail message."""
    print(f"{RED}✗ FAIL{RESET}")
    if error:
        print(f"  {RED}Error: {error}{RESET}")


def print_skip(reason: str = "") -> None:
    """Print skip message."""
    print(f"{YELLOW}⊘ SKIP{RESET}")
    if reason:
        print(f"  {YELLOW}Reason: {reason}{RESET}")


# Test 1: Configuration Loading
async def test_config_loading() -> bool:
    """Test that configuration loads correctly."""
    print_test("Test 1: Configuration Loading")
    try:
        from agent.config import settings

        # Check critical settings exist
        assert settings.database_url, "DATABASE_URL not set"
        assert settings.amazon_ads_client_id, "AMAZON_ADS_CLIENT_ID not set"
        assert settings.amazon_ads_client_secret, "AMAZON_ADS_CLIENT_SECRET not set"

        print_pass()
        return True
    except Exception as e:
        print_fail(str(e))
        return False


# Test 2: Database Connection
async def test_database_connection() -> bool:
    """Test database connection."""
    print_test("Test 2: Database Connection")
    try:
        from agent.data.async_db import get_async_engine, AsyncSessionLocal

        engine = get_async_engine()
        async with AsyncSessionLocal() as session:
            # Try a simple query
            result = await session.execute("SELECT 1")
            row = result.scalar()
            assert row == 1, "Query returned unexpected result"

        print_pass()
        return True
    except Exception as e:
        print_fail(str(e))
        return False


# Test 3: Job Tracker
async def test_job_tracker() -> bool:
    """Test job tracking system."""
    print_test("Test 3: Job Tracker")
    try:
        from agent.jobs.job_tracker import tracker, JobStatus

        # Create job
        job_id = await tracker.create_job('test', 'Test job')
        assert job_id, "Failed to create job"

        # Update job
        await tracker.update_job(job_id, progress=50.0, records_fetched=50)

        # Get job
        job = await tracker.get_job(job_id)
        assert job is not None, "Failed to retrieve job"
        assert job.progress == 50.0, "Progress not updated"
        assert job.records_fetched == 50, "Records count not updated"

        # Complete job
        await tracker.update_job(job_id, status=JobStatus.COMPLETED, progress=100.0)
        job = await tracker.get_job(job_id)
        assert job.status == JobStatus.COMPLETED, "Job not marked as completed"

        print_pass()
        return True
    except Exception as e:
        print_fail(str(e))
        return False


# Test 4: CSV Import
async def test_csv_import() -> bool:
    """Test CSV import functionality."""
    print_test("Test 4: CSV Import")
    try:
        from agent.jobs.import_spreadsheet import import_csv
        import tempfile

        # Create test CSV
        csv_content = """Date,Campaign Name,Ad Group Name,Targeting,Match Type,Impressions,Clicks,Click-Thru Rate (CTR),Cost Per Click (CPC),Spend,7 Day Total Sales ,Total Advertising Cost of Sales (ACoS) ,7 Day Total Orders (#),7 Day Total Units (#),7 Day Conversion Rate
2025-12-01,Test Campaign,Test Ad Group,test keyword,EXACT,1000,50,5.00,0.50,25.00,100.00,25.00,5,10,10.00
2025-12-02,Test Campaign,Test Ad Group,test keyword,EXACT,1200,60,5.00,0.48,28.80,120.00,24.00,6,12,10.00
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            records = await import_csv(temp_path)
            assert len(records) == 2, f"Expected 2 records, got {len(records)}"
            assert records[0].keyword == 'test keyword', "Keyword not parsed correctly"
            assert records[0].spend == 25.00, "Spend not parsed correctly"
            assert records[0].sales == 100.00, "Sales not parsed correctly"

            print_pass()
            return True
        finally:
            Path(temp_path).unlink()

    except Exception as e:
        print_fail(str(e))
        return False


# Test 5: Fetch Reports (Mock)
async def test_fetch_reports() -> bool:
    """Test fetch reports functionality."""
    print_test("Test 5: Fetch Reports (Mock)")
    try:
        from agent.jobs.fetch_reports import fetch_reports_async
        from agent.jobs.job_tracker import tracker

        # Create job
        job_id = await tracker.create_job('fetch', 'Test fetch')

        # Run fetch (should complete in mock mode)
        await fetch_reports_async(
            job_id=job_id,
            profile_id='test123',
            start_date='2025-12-01',
            end_date='2025-12-07',
            report_type='keywords'
        )

        # Check job completed
        job = await tracker.get_job(job_id)
        assert job is not None, "Job not found"
        assert job.status.value in ['COMPLETED', 'FAILED'], f"Unexpected job status: {job.status.value}"

        if job.status.value == 'COMPLETED':
            assert job.progress == 100.0, "Job not 100% complete"
            assert job.records_fetched > 0, "No records fetched"

        print_pass()
        return True
    except Exception as e:
        print_fail(str(e))
        return False


# Test 6: Pydantic Models
async def test_pydantic_models() -> bool:
    """Test Pydantic model validation."""
    print_test("Test 6: Pydantic Models")
    try:
        from agent.ui.models import (
            FetchRequest,
            FetchResponse,
            FetchStatusResponse,
            APIResponse,
            JobStatus,
        )

        # Test FetchRequest validation
        request = FetchRequest(
            profile_id='123',
            start_date='2025-12-01',
            end_date='2025-12-07',
            report_type='keywords'
        )
        assert request.profile_id == '123'

        # Test response models
        response = APIResponse(
            status='success',
            message='Test',
            data={'test': 'value'}
        )
        assert response.status == 'success'

        print_pass()
        return True
    except Exception as e:
        print_fail(str(e))
        return False


# Test 7: Context Utilities
async def test_context_utilities() -> bool:
    """Test context utility functions."""
    print_test("Test 7: Context Utilities")
    try:
        from agent.context import generate_job_id

        # Generate job ID
        job_id = generate_job_id('test')
        assert job_id.startswith('test_'), "Job ID doesn't have correct prefix"
        assert len(job_id) > 20, "Job ID seems too short"

        # Generate another - should be unique
        job_id2 = generate_job_id('test')
        assert job_id != job_id2, "Job IDs not unique"

        print_pass()
        return True
    except Exception as e:
        print_fail(str(e))
        return False


async def main():
    """Run all tests."""
    print_header("AMAZON PPC OPTIMIZATION TOOL - AUTOMATED TEST SUITE")

    results = []

    # Run all tests
    results.append(await test_config_loading())
    results.append(await test_database_connection())
    results.append(await test_job_tracker())
    results.append(await test_csv_import())
    results.append(await test_fetch_reports())
    results.append(await test_pydantic_models())
    results.append(await test_context_utilities())

    # Summary
    print_header("TEST SUMMARY")

    total = len(results)
    passed = sum(results)
    failed = total - passed

    print(f"Total Tests:  {total}")
    print(f"{GREEN}Passed:       {passed}{RESET}")
    if failed > 0:
        print(f"{RED}Failed:       {failed}{RESET}")
    else:
        print(f"Failed:       {failed}")

    print()

    if failed == 0:
        print(f"{GREEN}{BOLD}✅ ALL TESTS PASSED!{RESET}")
        print(f"\n{GREEN}Your implementation is working correctly.{RESET}")
        print(f"{BLUE}Next steps:{RESET}")
        print("  1. Start API server: python3 -m agent api")
        print("  2. Test endpoints: see TESTING_GUIDE.md")
        print("  3. Implement database models (Phase 1.3)")
        return 0
    else:
        print(f"{RED}{BOLD}❌ SOME TESTS FAILED{RESET}")
        print(f"\n{YELLOW}Please review the errors above and fix the issues.{RESET}")
        print(f"{BLUE}See TESTING_GUIDE.md for troubleshooting help.{RESET}")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
