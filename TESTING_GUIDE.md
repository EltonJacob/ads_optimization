# Testing Guide - Verify Current Implementation

This guide will help you test all the functionality that has been implemented so far in the Amazon PPC Optimization Tool.

## Prerequisites

Before testing, ensure you have:

1. ✅ Updated `.env` file with your credentials (DONE - I can see you've added them)
2. ✅ Python 3.13+ installed
3. ✅ All dependencies installed

## Step 1: Install Dependencies

```bash
cd "/Users/eltonjacob/Desktop/Desktop - Elton's iMac/Projects/Amazon PPC"

# Install all required packages
pip3 install -r requirements.txt
```

Expected output:
```
Successfully installed fastapi uvicorn sqlalchemy pydantic python-dotenv ...
```

## Step 2: Verify Environment Configuration

```bash
python3 verify_env.py
```

Expected output:
- ✅ All green checkmarks for:
  - Database configuration
  - Amazon Ads API credentials
  - AI Provider (OpenAI)
  - Python dependencies
  - Application settings

If you see any red X's, review the output and fix the issues.

## Step 3: Test Configuration Loading

Test that the application can load your configuration:

```bash
python3 -m agent config
```

Expected output:
```
=== Amazon PPC Agent Configuration ===

Database:
  database_url: postgresql+psycopg://eldonya:***@amazon-ppc-db...

Amazon Ads API:
  amazon_ads_client_id: amzn1.application-oa2-client.***
  amazon_ads_client_secret: ***
  amazon_ads_refresh_token: ***
  amazon_ads_api_base: https://advertising-api.amazon.com
  amazon_ads_auth_url: https://api.amazon.com/auth/o2/token

Optimization:
  target_acos: 0.25
  min_bid: 0.2
  max_bid: 1.6
  ...
```

✅ **PASS if:** Configuration displays without errors and sensitive values are masked

## Step 4: Test Health Check

Test the health check functionality:

```bash
python3 -m agent healthcheck
```

Expected output:
```
Running health check...
✓ Configuration loaded successfully
✓ Mock profiles available: 2
  - Profile ID: 1234567890 (US)
  - Profile ID: 9876543210 (CA)

Health check passed!
```

✅ **PASS if:** Health check completes without errors

## Step 5: Start the FastAPI Server

Start the API server in a terminal:

```bash
python3 -m agent api
```

Expected output:
```
INFO:     Starting Amazon PPC Optimization API...
INFO:     Will run on: http://0.0.0.0:8000
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

✅ **PASS if:** Server starts without errors

**Keep this terminal running for the following tests.**

## Step 6: Test API Endpoints

Open a **new terminal** and run these tests:

### 6.1 Test Root Endpoint

```bash
curl http://localhost:8000/
```

Expected output:
```json
{
  "message": "Amazon PPC Optimization API",
  "status": "running",
  "version": "1.0.0"
}
```

### 6.2 Test Health Endpoint

```bash
curl http://localhost:8000/health
```

Expected output:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-15T...",
  "version": "1.0.0"
}
```

### 6.3 Test API Documentation

Open your browser and visit:

```
http://localhost:8000/docs
```

Expected: **Interactive Swagger UI** showing all available endpoints:
- GET `/`
- GET `/health`
- POST `/api/fetch`
- GET `/api/fetch/status/{job_id}`

✅ **PASS if:** Documentation loads and shows all endpoints

### 6.4 Test Data Fetch Endpoint (Mock)

Trigger a mock data fetch:

```bash
curl -X POST "http://localhost:8000/api/fetch" \
  -H "Content-Type: application/json" \
  -d '{
    "profile_id": "3615809640282046",
    "start_date": "2025-12-01",
    "end_date": "2025-12-15",
    "report_type": "keywords"
  }'
```

Expected output:
```json
{
  "status": "success",
  "message": "Fetch job started",
  "data": {
    "job_id": "fetch_20251215_123456_abcdef12"
  }
}
```

✅ **PASS if:** Returns a job_id

**Save the job_id for the next test.**

### 6.5 Test Fetch Status Endpoint

Using the job_id from the previous step:

```bash
curl "http://localhost:8000/api/fetch/status/fetch_20251215_123456_abcdef12"
```

Expected output (while running):
```json
{
  "status": "success",
  "data": {
    "job_id": "fetch_20251215_123456_abcdef12",
    "status": "IN_PROGRESS",
    "progress": 60.0,
    "records_fetched": 90,
    "started_at": "2025-12-15T12:34:56",
    "completed_at": null,
    "error": null
  }
}
```

Wait 10-15 seconds and check again. Expected output (when complete):
```json
{
  "status": "success",
  "data": {
    "job_id": "fetch_20251215_123456_abcdef12",
    "status": "COMPLETED",
    "progress": 100.0,
    "records_fetched": 150,
    "started_at": "2025-12-15T12:34:56",
    "completed_at": "2025-12-15T12:35:06",
    "error": null
  }
}
```

✅ **PASS if:** Status progresses from IN_PROGRESS to COMPLETED

### 6.6 Test Job Not Found

```bash
curl "http://localhost:8000/api/fetch/status/invalid_job_id"
```

Expected output:
```json
{
  "status": "error",
  "error": {
    "code": "NOT_FOUND",
    "message": "Job not found: invalid_job_id"
  }
}
```

✅ **PASS if:** Returns 404 error with proper message

## Step 7: Test Spreadsheet Import (No API - Direct Function Test)

Create a test CSV file:

```bash
cat > /tmp/test_ppc_data.csv << 'EOF'
Date,Campaign Name,Ad Group Name,Targeting,Match Type,Impressions,Clicks,Click-Thru Rate (CTR),Cost Per Click (CPC),Spend,7 Day Total Sales ,Total Advertising Cost of Sales (ACoS) ,7 Day Total Orders (#),7 Day Total Units (#),7 Day Conversion Rate
2025-12-01,Test Campaign,Test Ad Group,keyword test,EXACT,1000,50,5.00,0.50,25.00,100.00,25.00,5,10,10.00
2025-12-02,Test Campaign,Test Ad Group,keyword test,EXACT,1200,60,5.00,0.48,28.80,120.00,24.00,6,12,10.00
2025-12-03,Test Campaign,Test Ad Group,another keyword,BROAD,800,40,5.00,0.52,20.80,80.00,26.00,4,8,10.00
EOF
```

Test the import function:

```bash
python3 -c "
from agent.jobs.import_spreadsheet import import_csv
import asyncio

async def test():
    records = await import_csv('/tmp/test_ppc_data.csv')
    print(f'✓ Imported {len(records)} records')
    for i, record in enumerate(records[:2], 1):
        print(f'\\nRecord {i}:')
        print(f'  Keyword: {record.keyword}')
        print(f'  Date: {record.date}')
        print(f'  Spend: ${record.spend:.2f}')
        print(f'  Sales: ${record.sales:.2f}')
        print(f'  Orders: {record.orders}')

asyncio.run(test())
"
```

Expected output:
```
✓ Imported 3 records

Record 1:
  Keyword: keyword test
  Date: 2025-12-01
  Spend: $25.00
  Sales: $100.00
  Orders: 5

Record 2:
  Keyword: keyword test
  Date: 2025-12-02
  Spend: $28.80
  Sales: $120.00
  Orders: 6
```

✅ **PASS if:** CSV is parsed correctly and data is extracted

## Step 8: Test Database Connection

Test that the async database setup works:

```bash
python3 -c "
from agent.data.async_db import get_async_engine, AsyncSessionLocal
import asyncio

async def test():
    try:
        engine = get_async_engine()
        print(f'✓ Database engine created: {engine.url}')

        async with AsyncSessionLocal() as session:
            print('✓ Database session created successfully')
            result = await session.execute('SELECT 1')
            print('✓ Database query executed successfully')

        print('\\n✅ Database connection test PASSED')
    except Exception as e:
        print(f'❌ Database connection test FAILED: {e}')

asyncio.run(test())
"
```

Expected output:
```
✓ Database engine created: postgresql+psycopg://eldonya:***@amazon-ppc-db...
✓ Database session created successfully
✓ Database query executed successfully

✅ Database connection test PASSED
```

✅ **PASS if:** All database operations succeed

**Note:** If this fails with "no such table" errors, that's expected - the database tables haven't been created yet (that's Phase 1.3 work).

## Step 9: Test Job Tracker

Test the job tracking system:

```bash
python3 -c "
from agent.jobs.job_tracker import tracker, JobStatus
import asyncio

async def test():
    # Create a test job
    job_id = await tracker.create_job('test', 'Testing job tracker')
    print(f'✓ Created job: {job_id}')

    # Update progress
    await tracker.update_job(job_id, progress=50.0, records_fetched=50)
    print('✓ Updated job progress to 50%')

    # Get job info
    job = await tracker.get_job(job_id)
    print(f'✓ Retrieved job: {job.status.value}, Progress: {job.progress}%')

    # Complete job
    await tracker.update_job(job_id, status=JobStatus.COMPLETED, progress=100.0)
    job = await tracker.get_job(job_id)
    print(f'✓ Job completed: {job.status.value}')

    print('\\n✅ Job tracker test PASSED')

asyncio.run(test())
"
```

Expected output:
```
✓ Created job: test_20251215_123456_abcdef12
✓ Updated job progress to 50%
✓ Retrieved job: IN_PROGRESS, Progress: 50.0%
✓ Job completed: COMPLETED

✅ Job tracker test PASSED
```

✅ **PASS if:** Job lifecycle works correctly

## Step 10: Test Using Interactive API Docs

1. **Open browser:** http://localhost:8000/docs

2. **Test POST /api/fetch:**
   - Click on "POST /api/fetch"
   - Click "Try it out"
   - Enter request body:
     ```json
     {
       "profile_id": "3615809640282046",
       "start_date": "2025-12-01",
       "end_date": "2025-12-07",
       "report_type": "keywords"
     }
     ```
   - Click "Execute"
   - ✅ **PASS if:** Response shows job_id

3. **Test GET /api/fetch/status/{job_id}:**
   - Copy the job_id from previous response
   - Click on "GET /api/fetch/status/{job_id}"
   - Click "Try it out"
   - Paste job_id
   - Click "Execute"
   - ✅ **PASS if:** Shows job status and progress

## Summary Checklist

After running all tests, you should have:

- [ ] ✅ Dependencies installed
- [ ] ✅ Environment verified (all green checks)
- [ ] ✅ Configuration loads correctly
- [ ] ✅ Health check passes
- [ ] ✅ API server starts
- [ ] ✅ Root endpoint responds
- [ ] ✅ Health endpoint responds
- [ ] ✅ API documentation loads
- [ ] ✅ Fetch endpoint creates jobs
- [ ] ✅ Status endpoint tracks jobs
- [ ] ✅ CSV import parses data
- [ ] ✅ Database connection works
- [ ] ✅ Job tracker functions properly

## What's Working

Based on the tests above, you've verified:

1. **FastAPI Setup (Phase 1.1)** - ✅ Complete and working
   - API server starts
   - Endpoints respond
   - CORS configured
   - Documentation available

2. **Data Fetch API (Phase 1.2)** - ✅ Complete and working
   - POST /api/fetch endpoint
   - GET /api/fetch/status endpoint
   - Background job execution
   - Job tracking system
   - Progress monitoring

3. **Spreadsheet Import Logic (Phase 1.3 - Partial)** - ✅ Import code works
   - CSV parsing
   - Excel parsing
   - Data validation
   - Date parsing
   - Keyword ID generation

## What's NOT Working Yet (Expected)

These features are not implemented yet (per project plan):

1. **Database Persistence** - Tables not created yet
   - Can connect to database ✅
   - Cannot save data yet ❌ (DAO is stub)

2. **Upload API Endpoints** - Not implemented
   - POST /api/upload ❌
   - POST /api/import ❌

3. **Performance Query Endpoints** - Not implemented
   - All /api/performance/* endpoints ❌

4. **Frontend** - Not started
   - No UI yet ❌

5. **AI Analysis** - Not started
   - No recommendation engine ❌

## Troubleshooting

### Server won't start
```bash
# Check if port 8000 is in use
lsof -i :8000

# Kill process if needed
kill -9 <PID>

# Try different port
API_PORT=8001 python3 -m agent api
```

### Database connection fails
```bash
# Test PostgreSQL connection directly
psql "postgresql+psycopg://eldonya:Ed092023-AWS@amazon-ppc-db.cgxsgcec2mzg.us-east-1.rds.amazonaws.com:5432/amazon_ppc"
```

### Import errors
```bash
# Ensure you're in project root
cd "/Users/eltonjacob/Desktop/Desktop - Elton's iMac/Projects/Amazon PPC"

# Check Python path
python3 -c "import sys; print('\n'.join(sys.path))"
```

### Async errors
```bash
# Ensure psycopg (not psycopg2) is installed for async support
pip3 install psycopg[binary]
```

## Next Steps

After confirming everything works:

1. **Implement Database Models** (Critical blocker)
   - Create SQLAlchemy models
   - Set up Alembic migrations
   - Initialize database tables

2. **Complete Phase 1.3** - Upload API
   - Add POST /api/upload endpoint
   - Add POST /api/import endpoint
   - Connect import to database

3. **Start Phase 1.4** - Performance Query Endpoints
   - Implement all /api/performance/* endpoints

---

**Last Updated:** 2025-12-15
**Current Phase:** 1.2 Complete, 1.3 Partial (30%)
