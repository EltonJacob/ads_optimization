# Upload & Import API Documentation

## Overview

The Upload & Import API provides endpoints for uploading spreadsheet files (CSV/Excel) containing keyword performance data and importing them into the database. This serves as a fallback when the Amazon Ads API times out or is unavailable.

## Endpoints

### 1. Upload File
**POST** `/api/upload`

Upload a CSV or Excel file containing keyword performance data.

#### Request

**Content-Type:** `multipart/form-data`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file` | File | Yes | CSV or Excel file (.csv, .xlsx, .xls) |
| `profile_id` | string | Yes | Amazon Ads profile ID for organizing uploads |

#### Response

```json
{
  "upload_id": "upload_20251216_150212_14358",
  "filename": "keywords_data.csv",
  "file_type": ".csv",
  "size_bytes": 15240,
  "upload_path": "data/uploads/profile_123/upload_20251216_150212_14358.csv",
  "uploaded_at": "2025-12-16T15:02:12.014660",
  "message": "File uploaded successfully. Use upload_id 'upload_20251216_150212_14358' to import."
}
```

#### Error Responses

**400 Bad Request** - Invalid file type or size
```json
{
  "detail": "Unsupported file type: .txt. Allowed types: .csv, .xlsx, .xls"
}
```

```json
{
  "detail": "File too large: 150.5MB. Maximum allowed: 100MB"
}
```

#### Example

```bash
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@keywords_data.csv" \
  -F "profile_id=profile_123"
```

---

### 2. Preview Upload
**GET** `/api/upload/{upload_id}/preview`

Preview uploaded file contents and validate that all required columns are present.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `upload_id` | string | Yes | Upload ID returned from POST /api/upload |

#### Response

```json
{
  "upload_id": "upload_20251216_150212_14358",
  "filename": "upload_20251216_150212_14358.csv",
  "total_rows": 150,
  "preview_rows": [
    {
      "row_number": 1,
      "data": {
        "keyword": "running shoes",
        "match type": "exact",
        "impressions": "1000",
        "clicks": "50",
        "spend": "25.50",
        "sales": "150.00",
        "orders": "3"
      }
    }
  ],
  "detected_columns": [
    "keyword",
    "match type",
    "impressions",
    "clicks",
    "spend",
    "sales",
    "orders"
  ],
  "missing_columns": [],
  "validation_errors": []
}
```

#### With Validation Errors

```json
{
  "upload_id": "upload_20251216_150212_14358",
  "filename": "upload_20251216_150212_14358.csv",
  "total_rows": 150,
  "preview_rows": [...],
  "detected_columns": ["keyword", "impressions"],
  "missing_columns": ["clicks", "spend", "sales", "orders"],
  "validation_errors": [
    {
      "field": "columns",
      "message": "Missing required columns: clicks, spend, sales, orders"
    }
  ]
}
```

#### Example

```bash
curl -X GET "http://localhost:8000/api/upload/upload_20251216_150212_14358/preview"
```

---

### 3. Import File
**POST** `/api/import`

Import an uploaded spreadsheet file into the database as a background job.

#### Request

**Content-Type:** `application/json`

```json
{
  "upload_id": "upload_20251216_150212_14358",
  "profile_id": "profile_123",
  "start_date": "2025-11-01",
  "end_date": "2025-11-30"
}
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `upload_id` | string | Yes | Upload ID from POST /api/upload |
| `profile_id` | string | Yes | Amazon Ads profile ID |
| `start_date` | string (YYYY-MM-DD) | No | Start date filter (optional) |
| `end_date` | string (YYYY-MM-DD) | No | End date filter (optional) |

#### Response

```json
{
  "success": true,
  "job_id": "import_20251216_150212_cdf429bb",
  "rows_processed": 0,
  "rows_added": 0,
  "rows_skipped": 0,
  "errors": [],
  "message": "Import job started. Monitor progress at /api/import/status/import_20251216_150212_cdf429bb"
}
```

#### Error Responses

**404 Not Found** - Upload not found
```json
{
  "detail": "Upload upload_invalid_id not found"
}
```

**400 Bad Request** - Missing required columns
```json
{
  "detail": "Missing required columns: clicks, spend, sales, orders. Please ensure your file has: keyword, impressions, clicks, spend, sales, orders"
}
```

#### Example

```bash
curl -X POST "http://localhost:8000/api/import" \
  -H "Content-Type: application/json" \
  -d '{
    "upload_id": "upload_20251216_150212_14358",
    "profile_id": "profile_123"
  }'
```

---

### 4. Import Status
**GET** `/api/import/status/{job_id}`

Get the current status of an import job.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `job_id` | string | Yes | Job ID returned from POST /api/import |

#### Response

```json
{
  "job_id": "import_20251216_150212_cdf429bb",
  "status": "completed",
  "progress": 100.0,
  "rows_processed": 150,
  "rows_added": 145,
  "rows_skipped": 5,
  "errors": [],
  "started_at": "2025-12-16T15:02:12.039792",
  "completed_at": "2025-12-16T15:02:15.123456"
}
```

#### Job Status Values

| Status | Description |
|--------|-------------|
| `pending` | Job is queued but not yet started |
| `in_progress` | Job is currently running |
| `completed` | Job finished successfully |
| `failed` | Job failed with errors |
| `timeout` | Job exceeded time limit |

#### Example

```bash
curl -X GET "http://localhost:8000/api/import/status/import_20251216_150212_cdf429bb"
```

---

## File Format Requirements

### Required Columns

All uploaded files must contain these columns (case-insensitive):

- `keyword` - Keyword text
- `impressions` - Number of impressions (integer)
- `clicks` - Number of clicks (integer)
- `spend` - Amount spent (float, can include $ and commas)
- `sales` - Sales revenue (float, can include $ and commas)
- `orders` - Number of orders/conversions (integer)

### Optional Columns

These columns are optional but recommended:

- `date` - Date of the data (YYYY-MM-DD format)
- `keyword_id` or `keywordid` - Unique keyword identifier
- `match type` or `match_type` - Match type (exact, phrase, broad)
- `campaign` or `campaign name` - Campaign name
- `ad group` or `ad group name` - Ad group name
- `state` - Keyword state (enabled, paused, archived)
- `bid` - Current bid amount

### Supported File Formats

- **CSV** (`.csv`) - Comma-separated values with UTF-8 encoding
- **Excel** (`.xlsx`, `.xls`) - Microsoft Excel format

### File Size Limits

- Maximum file size: 100MB
- Recommended: Split large files into smaller batches

---

## File Format Examples

### Example 1: Standard Format

```csv
keyword,match type,impressions,clicks,spend,sales,orders,state,bid
running shoes,exact,1000,50,25.50,150.00,3,enabled,0.50
nike sneakers,phrase,800,30,15.75,90.00,2,enabled,0.45
athletic footwear,broad,1200,45,22.00,120.00,2,enabled,0.40
```

### Example 2: Amazon Ads Export Format

```csv
Campaign,Ad Group,Keyword,Match Type,Impressions,Clicks,Spend (USD),Sales (USD),Orders,State
Fall Sale,Running Shoes,running shoes,Exact,1000,50,$25.50,$150.00,3,enabled
Fall Sale,Running Shoes,nike sneakers,Phrase,800,30,$15.75,$90.00,2,enabled
```

### Example 3: Minimal Format

```csv
keyword,impressions,clicks,spend,sales,orders
running shoes,1000,50,25.50,150.00,3
nike sneakers,800,30,15.75,90.00,2
```

---

## Workflow

### Complete Upload & Import Workflow

```bash
# 1. Upload file
UPLOAD_RESPONSE=$(curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@keywords_data.csv" \
  -F "profile_id=profile_123")

UPLOAD_ID=$(echo $UPLOAD_RESPONSE | jq -r '.upload_id')

# 2. Preview file (optional but recommended)
curl "http://localhost:8000/api/upload/${UPLOAD_ID}/preview" | jq '.'

# 3. Start import
IMPORT_RESPONSE=$(curl -X POST "http://localhost:8000/api/import" \
  -H "Content-Type: application/json" \
  -d "{\"upload_id\": \"${UPLOAD_ID}\", \"profile_id\": \"profile_123\"}")

JOB_ID=$(echo $IMPORT_RESPONSE | jq -r '.job_id')

# 4. Monitor import status
while true; do
  STATUS=$(curl -s "http://localhost:8000/api/import/status/${JOB_ID}" | jq -r '.status')
  if [ "$STATUS" = "completed" ]; then
    echo "Import completed!"
    break
  elif [ "$STATUS" = "failed" ]; then
    echo "Import failed!"
    break
  fi
  sleep 2
done

# 5. Check final results
curl "http://localhost:8000/api/import/status/${JOB_ID}" | jq '.'
```

---

## Error Handling

### Common Errors

#### 1. File Type Not Supported

```json
{
  "detail": "Unsupported file type: .pdf. Allowed types: .csv, .xlsx, .xls"
}
```

**Solution:** Convert your file to CSV or Excel format.

#### 2. File Too Large

```json
{
  "detail": "File too large: 150.5MB. Maximum allowed: 100MB"
}
```

**Solution:** Split your file into smaller chunks or filter the data to reduce size.

#### 3. Missing Required Columns

```json
{
  "detail": "Missing required columns: clicks, spend, sales, orders. Please ensure your file has: keyword, impressions, clicks, spend, sales, orders"
}
```

**Solution:** Add the missing columns to your file or use a template that includes all required fields.

#### 4. No Valid Records

```json
{
  "job_id": "import_20251216_150212_cdf429bb",
  "status": "completed",
  "rows_processed": 0,
  "rows_added": 0,
  "rows_skipped": 100,
  "errors": ["No valid records found in file"]
}
```

**Solution:** Check your file format and ensure data is in the correct columns.

---

## Best Practices

### 1. Always Preview Before Import

Use the preview endpoint to validate your file structure before starting an import job.

### 2. Use Meaningful Profile IDs

Organize your uploads by profile_id to keep data from different accounts separate.

### 3. Monitor Import Status

Poll the status endpoint to track import progress and catch errors early.

### 4. Handle Errors Gracefully

Check the `validation_errors` array in the preview response and the `errors` array in the status response.

### 5. Clean Up Old Uploads

Periodically remove old uploaded files from `data/uploads/` to save disk space.

---

## Testing

Run the included test script to verify the upload and import functionality:

```bash
./test_upload_api.sh
```

This script will:
1. Upload a sample CSV file
2. Preview the uploaded file
3. Import the file
4. Monitor import status
5. Test error handling with an invalid file type

---

## Integration with Frontend

### React/Next.js Example

```typescript
// Upload file
const uploadFile = async (file: File, profileId: string) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('profile_id', profileId);

  const response = await fetch('http://localhost:8000/api/upload', {
    method: 'POST',
    body: formData,
  });

  return await response.json();
};

// Preview upload
const previewUpload = async (uploadId: string) => {
  const response = await fetch(
    `http://localhost:8000/api/upload/${uploadId}/preview`
  );
  return await response.json();
};

// Import file
const importFile = async (uploadId: string, profileId: string) => {
  const response = await fetch('http://localhost:8000/api/import', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ upload_id: uploadId, profile_id: profileId }),
  });
  return await response.json();
};

// Check import status
const checkImportStatus = async (jobId: string) => {
  const response = await fetch(
    `http://localhost:8000/api/import/status/${jobId}`
  );
  return await response.json();
};
```

---

## Security Considerations

1. **File Validation:** All uploaded files are validated for type and size
2. **Path Sanitization:** Upload paths are sanitized to prevent directory traversal
3. **Resource Limits:** File size limited to 100MB to prevent DoS attacks
4. **Async Processing:** Large imports run in background to prevent blocking

---

## Performance

- **File Upload:** < 1 second for files up to 10MB
- **Preview Generation:** < 2 seconds for files with 10,000 rows
- **Import Processing:** ~1000 rows per second (varies by system)

---

## Related Endpoints

- [POST /api/fetch](DATA_FETCH_API_IMPLEMENTATION.md) - Fetch data from Amazon Ads API
- [GET /api/fetch/status/{job_id}](DATA_FETCH_API_IMPLEMENTATION.md) - Check fetch job status

---

**Version:** 1.0
**Last Updated:** 2025-12-16
**Status:** Production Ready
