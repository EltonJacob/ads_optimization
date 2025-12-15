# How to Test - Simple Step-by-Step Guide

This is a simplified guide to test what's currently working in your Amazon PPC Optimization Tool.

## Prerequisites

Your `.env` file is already configured with:
- ✅ PostgreSQL database connection
- ✅ Amazon Ads API credentials
- ✅ OpenAI API key

## Step 1: Install Dependencies

First, install all required Python packages:

```bash
cd "/Users/eltonjacob/Desktop/Desktop - Elton's iMac/Projects/Amazon PPC"

pip3 install -r requirements.txt
```

**Expected output:**
```
Successfully installed fastapi-0.104.1 uvicorn-0.24.0 sqlalchemy-2.0.23 ...
```

**If you see errors:** Make sure you have pip3 installed:
```bash
python3 -m ensurepip --upgrade
```

## Step 2: Verify Environment

Run the environment verification script:

```bash
python3 verify_env.py
```

**What to look for:**
- ✅ All green checkmarks for:
  - Database configuration
  - Amazon Ads API credentials (should show masked values)
  - OpenAI configuration
  - Python dependencies

**If you see errors about missing packages:** Go back to Step 1 and reinstall dependencies.

## Step 3: Test Basic Commands

### Test Configuration Display

```bash
python3 -m agent config
```

**Expected:** Should display your configuration with masked credentials

### Test Health Check

```bash
python3 -m agent healthcheck
```

**Expected:**
```
Running health check...
✓ Configuration loaded successfully
✓ Mock profiles available: 2
  - Profile ID: 1234567890 (US)
  - Profile ID: 9876543210 (CA)

Health check passed!
```

## Step 4: Start the API Server

Start the FastAPI server:

```bash
python3 -m agent api
```

**Expected output:**
```
INFO:     Starting Amazon PPC Optimization API...
INFO:     Will run on: http://0.0.0.0:8000
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

✅ **SUCCESS:** If you see this, your API server is running!

**Keep this terminal window open** - the server needs to stay running for the next tests.

## Step 5: Test API Endpoints

Open a **NEW terminal window** and run these tests:

### Test 1: Root Endpoint

```bash
curl http://localhost:8000/
```

**Expected:**
```json
{
  "message": "Amazon PPC Optimization API",
  "status": "running",
  "version": "1.0.0"
}
```

### Test 2: Health Endpoint

```bash
curl http://localhost:8000/health
```

**Expected:**
```json
{
  "status": "healthy",
  "timestamp": "2025-12-15T...",
  "version": "1.0.0"
}
```

### Test 3: Trigger Data Fetch

```bash
curl -X POST "http://localhost:8000/api/fetch" \
  -H "Content-Type: application/json" \
  -d '{
    "profile_id": "3615809640282046",
    "start_date": "2025-12-01",
    "end_date": "2025-12-07",
    "report_type": "keywords"
  }'
```

**Expected:**
```json
{
  "status": "success",
  "message": "Fetch job started",
  "data": {
    "job_id": "fetch_20251215_123456_abc123"
  }
}
```

✅ **SUCCESS:** Copy the `job_id` from the response - you'll need it for the next test!

### Test 4: Check Fetch Status

Replace `YOUR_JOB_ID` with the actual job_id from the previous test:

```bash
curl "http://localhost:8000/api/fetch/status/YOUR_JOB_ID"
```

**Example:**
```bash
curl "http://localhost:8000/api/fetch/status/fetch_20251215_123456_abc123"
```

**Expected (while running):**
```json
{
  "status": "success",
  "data": {
    "job_id": "fetch_20251215_123456_abc123",
    "status": "IN_PROGRESS",
    "progress": 42.857142857142854,
    "records_fetched": 60,
    "started_at": "2025-12-15T...",
    "completed_at": null,
    "error": null
  }
}
```

**Wait 10-15 seconds and check again.** Eventually you should see:

```json
{
  "status": "success",
  "data": {
    "job_id": "fetch_20251215_123456_abc123",
    "status": "COMPLETED",
    "progress": 100.0,
    "records_fetched": 140,
    "started_at": "2025-12-15T...",
    "completed_at": "2025-12-15T...",
    "error": null
  }
}
```

✅ **SUCCESS:** If the status changes from IN_PROGRESS to COMPLETED, the fetch system is working!

## Step 6: Test API Documentation

Open your web browser and visit:

```
http://localhost:8000/docs
```

**What you should see:**
- Interactive Swagger UI interface
- List of all available endpoints:
  - GET `/` - Root endpoint
  - GET `/health` - Health check
  - POST `/api/fetch` - Fetch data
  - GET `/api/fetch/status/{job_id}` - Check fetch status

**Try it out:**
1. Click on "POST /api/fetch"
2. Click "Try it out"
3. Edit the request body with your profile ID
4. Click "Execute"
5. See the response with a job_id

✅ **SUCCESS:** If the interactive docs work, you've verified the entire API layer!

## Step 7: Test Database Connection

Test that you can connect to your PostgreSQL database:

```bash
python3 -c "
from agent.config import settings
print('Database URL:', settings.database_url.split('@')[-1])  # Hide password
print('Attempting connection...')

from agent.data.async_db import get_async_engine, AsyncSessionLocal
import asyncio

async def test():
    try:
        engine = get_async_engine()
        print('✓ Engine created')

        async with AsyncSessionLocal() as session:
            print('✓ Session created')
            result = await session.execute('SELECT version()')
            version = result.scalar()
            print(f'✓ Connected! PostgreSQL version: {version[:50]}...')
    except Exception as e:
        print(f'✗ Error: {e}')

asyncio.run(test())
"
```

**Expected:**
```
Database URL: amazon-ppc-db.cgxsgcec2mzg.us-east-1.rds.amazonaws.com:5432/amazon_ppc
Attempting connection...
✓ Engine created
✓ Session created
✓ Connected! PostgreSQL version: PostgreSQL 16.x on x86_64-pc-linux-gnu...
```

✅ **SUCCESS:** If you see the PostgreSQL version, your database connection works!

## What's Working - Summary

If all the above tests passed, you've verified:

| Component | Status | What It Does |
|-----------|--------|--------------|
| **Environment Config** | ✅ Working | Loads `.env` file and validates settings |
| **CLI Commands** | ✅ Working | `config`, `healthcheck`, `api` commands |
| **FastAPI Server** | ✅ Working | HTTP server on port 8000 |
| **API Endpoints** | ✅ Working | Root, health, fetch, status endpoints |
| **Background Jobs** | ✅ Working | Async job execution with progress tracking |
| **Job Tracking** | ✅ Working | In-memory job status storage |
| **Database Connection** | ✅ Working | Can connect to PostgreSQL |
| **API Documentation** | ✅ Working | Interactive Swagger UI |

## What's NOT Working Yet (Expected)

These features haven't been implemented yet:

| Component | Status | Why |
|-----------|--------|-----|
| **Data Persistence** | ❌ Not Implemented | Database tables not created yet |
| **Upload Endpoints** | ❌ Not Implemented | POST /api/upload, /api/import missing |
| **Performance Queries** | ❌ Not Implemented | GET /api/performance/* not built |
| **Frontend UI** | ❌ Not Implemented | No Next.js app yet |
| **AI Analysis** | ❌ Not Implemented | Recommendation engine not built |

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'fastapi'"

**Solution:**
```bash
pip3 install -r requirements.txt
```

### Issue: "Address already in use" when starting API server

**Solution:** Port 8000 is being used by another process. Either:

1. Kill the other process:
```bash
lsof -ti:8000 | xargs kill -9
```

2. Or use a different port:
```bash
API_PORT=8001 python3 -m agent api
```

### Issue: Database connection fails

**Solution:** Check that your database is accessible:

```bash
# Test direct connection (will prompt for password)
psql -h amazon-ppc-db.cgxsgcec2mzg.us-east-1.rds.amazonaws.com -U eldonya -d amazon_ppc
```

If this fails, check:
- Database is running
- Security group allows your IP
- Credentials are correct in `.env`

### Issue: "Connection refused" when testing endpoints

**Solution:** Make sure the API server is running (Step 4). You should see "Uvicorn running..." in the terminal.

## Next Steps

After verifying everything works:

1. **Implement Database Models** (Critical blocker)
   - Create SQLAlchemy models for all tables
   - Set up Alembic migrations
   - Initialize database schema

2. **Complete Upload API** (Phase 1.3)
   - Add POST /api/upload endpoint
   - Add POST /api/import endpoint
   - Connect import logic to database

3. **Start Frontend** (Phase 2)
   - Initialize Next.js project
   - Build data import interface
   - Create dashboard

## Quick Test Summary

✅ If you got this far and all tests passed, **congratulations!**

Your implementation is working correctly for Phase 1.1 and 1.2:
- ✅ FastAPI server running
- ✅ API endpoints responding
- ✅ Background job system working
- ✅ Database connection established
- ✅ Configuration management working

The foundation is solid. Now you can move on to implementing the remaining features!

---

**Need help?** See:
- [TESTING_GUIDE.md](TESTING_GUIDE.md) - Detailed testing instructions
- [README.md](README.md) - Project overview
- [project_plan.txt](project_plan.txt) - Complete implementation plan
