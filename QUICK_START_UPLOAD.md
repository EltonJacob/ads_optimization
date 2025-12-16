# Quick Start: File Upload & Import

This guide helps you quickly upload and import keyword performance data when the Amazon Ads API is unavailable.

## Prerequisites

1. FastAPI server running on `http://localhost:8000`
2. A CSV or Excel file with keyword performance data

## Step-by-Step Guide

### Step 1: Prepare Your File

Your file must contain these columns (case-insensitive):

```
keyword, impressions, clicks, spend, sales, orders
```

Optional but recommended: `match type`, `campaign`, `date`, `state`, `bid`

**Example CSV:**
```csv
keyword,match type,impressions,clicks,spend,sales,orders
running shoes,exact,1000,50,25.50,150.00,3
nike sneakers,phrase,800,30,15.75,90.00,2
```

### Step 2: Upload Your File

```bash
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@your_file.csv" \
  -F "profile_id=your_profile_id"
```

**Save the `upload_id` from the response!**

### Step 3: Preview (Optional but Recommended)

```bash
curl "http://localhost:8000/api/upload/YOUR_UPLOAD_ID/preview" | jq '.'
```

Check the `validation_errors` array. If empty, proceed to import.

### Step 4: Import the File

```bash
curl -X POST "http://localhost:8000/api/import" \
  -H "Content-Type: application/json" \
  -d '{
    "upload_id": "YOUR_UPLOAD_ID",
    "profile_id": "your_profile_id"
  }'
```

**Save the `job_id` from the response!**

### Step 5: Monitor Import Progress

```bash
curl "http://localhost:8000/api/import/status/YOUR_JOB_ID" | jq '.'
```

Keep checking until `status` is `"completed"` or `"failed"`.

## One-Line Testing

Run the automated test script:

```bash
./test_upload_api.sh
```

This will test all functionality with a sample file.

## Common Issues

### "Missing required columns"
→ Add the required columns to your file: keyword, impressions, clicks, spend, sales, orders

### "File too large"
→ Split your file into smaller chunks (max 100MB)

### "Unsupported file type"
→ Only CSV (.csv) and Excel (.xlsx, .xls) are supported

### Import shows 0 rows added
→ Check that your file has data beyond the header row and that columns are named correctly

## Need Help?

- Full API docs: [UPLOAD_API_DOCUMENTATION.md](UPLOAD_API_DOCUMENTATION.md)
- Project plan: [project_plan.txt](project_plan.txt)
- API documentation: http://localhost:8000/docs (when server is running)

---

**Quick Tip:** Always preview your file before importing to catch validation errors early!
