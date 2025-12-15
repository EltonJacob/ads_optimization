# FastAPI Setup & Testing Guide

## CORS Middleware Configuration - Complete! ✅

The FastAPI application has been successfully configured with CORS middleware for frontend integration.

## What Was Implemented

### 1. **Dependencies Added** ([requirements.txt](requirements.txt))
```
fastapi>=0.115,<0.116
uvicorn[standard]>=0.32,<0.33
pydantic>=2.0,<3.0
python-multipart>=0.0.9,<0.1.0
sqlalchemy[asyncio]>=2.0,<3.0
aiosqlite>=0.20,<0.21
asyncpg>=0.29,<0.30
```

### 2. **FastAPI Application** ([agent/ui/api.py](agent/ui/api.py))
- FastAPI app instance with proper configuration
- **CORS middleware configured** to allow requests from:
  - `http://localhost:3000` (Next.js default)
  - `http://localhost:3001` (alternative port)
  - `http://127.0.0.1:3000` and `3001`
- Allows all HTTP methods (GET, POST, PUT, DELETE, etc.)
- Allows credentials (cookies, authorization headers)
- Allows all headers
- Basic health check endpoints: `/` and `/api/health`

### 3. **Pydantic Models** ([agent/ui/models.py](agent/ui/models.py))
Complete request/response models for:
- Health checks
- Data fetching (FetchRequest, FetchResponse, FetchStatusResponse)
- File uploads (UploadResponse, ImportRequest, ImportResponse)
- Performance data (KeywordPerformance, PerformanceSummary)
- Recommendations (BidRecommendation, KeywordPauseRecommendation, etc.)
- Decisions and audit logs

### 4. **Async Database Session** ([agent/data/async_db.py](agent/data/async_db.py))
- Async SQLAlchemy session management
- FastAPI dependency injection ready (`get_db_session`)
- Supports both SQLite (aiosqlite) and PostgreSQL (asyncpg)
- Automatic URL conversion from sync to async

### 5. **CLI Command** ([agent/__main__.py](agent/__main__.py))
New `api` command to launch the FastAPI server:
```bash
python -m agent api              # Start on default port 8000
python -m agent api --port 3001  # Custom port
python -m agent api --reload     # Development mode with auto-reload
```

## How to Test

### Step 1: Recreate Virtual Environment
```bash
# Remove broken venv
rm -rf .venv

# Create new virtual environment (requires Python 3.13)
python3.13 -m venv .venv

# Activate it
source .venv/bin/activate
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Launch the API Server
```bash
# Development mode (with auto-reload)
python -m agent api --reload

# Production mode
python -m agent api
```

### Step 4: Test the Endpoints
Once the server is running, you can test it:

**Using curl:**
```bash
# Health check
curl http://localhost:8000/

# API health endpoint
curl http://localhost:8000/api/health
```

**Using browser:**
- Open: http://localhost:8000
- API docs: http://localhost:8000/docs (Swagger UI)
- ReDoc: http://localhost:8000/redoc

### Step 5: Test CORS from Frontend
Create a simple test HTML file:

```html
<!DOCTYPE html>
<html>
<head>
    <title>CORS Test</title>
</head>
<body>
    <h1>Testing CORS</h1>
    <button onclick="testAPI()">Test API</button>
    <pre id="result"></pre>

    <script>
        async function testAPI() {
            try {
                const response = await fetch('http://localhost:8000/api/health');
                const data = await response.json();
                document.getElementById('result').textContent = JSON.stringify(data, null, 2);
            } catch (error) {
                document.getElementById('result').textContent = 'Error: ' + error.message;
            }
        }
    </script>
</body>
</html>
```

Serve this HTML on a different port (e.g., using Python's http.server on port 3000):
```bash
python3 -m http.server 3000
```

Then open http://localhost:3000 and click the button. If CORS is working, you'll see the API response!

## What CORS Middleware Does

The CORS middleware configuration in [agent/ui/api.py](agent/ui/api.py:38-48) adds these HTTP headers to all responses:

```
Access-Control-Allow-Origin: http://localhost:3000
Access-Control-Allow-Credentials: true
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS, PATCH
Access-Control-Allow-Headers: *
```

This tells the browser:
- ✅ Allow requests from localhost:3000 (your Next.js frontend)
- ✅ Allow cookies and authorization headers
- ✅ Allow all HTTP methods
- ✅ Allow all request headers

## Next Steps (Phase 1.2 - 1.4)

Now that CORS is configured, the next phases are:

1. **Phase 1.2**: Data Fetch API Endpoints
   - POST /api/fetch
   - GET /api/fetch/status/{job_id}

2. **Phase 1.3**: Spreadsheet Upload API
   - POST /api/upload
   - POST /api/import

3. **Phase 1.4**: Performance Query Endpoints
   - GET /api/performance/{profile_id}
   - GET /api/performance/{profile_id}/summary
   - GET /api/performance/{profile_id}/keywords
   - GET /api/performance/{profile_id}/trends

## Troubleshooting

### Issue: ModuleNotFoundError
**Solution:** Recreate the virtual environment and install dependencies

### Issue: CORS errors in browser
**Solution:** Check that:
1. Frontend is running on port 3000 or 3001
2. Backend is running on port 8000
3. The frontend origin is in the `allow_origins` list in api.py

### Issue: Can't connect to database
**Solution:** Check your `.env` file has the correct `DATABASE_URL`

## Architecture Summary

```
Frontend (Next.js)           Backend (FastAPI)
Port 3000                    Port 8000
     |                            |
     |-------- HTTP Request ----->|
     |    (blocked by browser)    |
     |                            |
     |<--- CORS Headers ----------|
     |    (browser allows it!)    |
     |                            |
     |<--- JSON Response ---------|
```

The CORS middleware makes cross-origin requests work seamlessly between your frontend and backend!
