#!/bin/bash

# Test script for Upload and Import API endpoints
# Usage: ./test_upload_api.sh

set -e

API_URL="http://localhost:8000"
PROFILE_ID="test_profile_123"

echo "======================================================================"
echo "Testing Upload & Import API Endpoints"
echo "======================================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_info() {
    echo -e "${BLUE}→ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check if API is running
print_info "Checking if API is running..."
if ! curl -s "${API_URL}/api/health" > /dev/null; then
    print_error "API is not running at ${API_URL}"
    echo "Please start the API server with: uvicorn agent.ui.api:app --reload"
    exit 1
fi
print_success "API is running"
echo ""

# Create a sample CSV file for testing
print_info "Creating sample CSV file..."
SAMPLE_FILE="data/uploads/sample_test.csv"
mkdir -p "data/uploads"

cat > "$SAMPLE_FILE" << 'EOF'
keyword,match type,impressions,clicks,spend,sales,orders,state,bid
running shoes,exact,1000,50,25.50,150.00,3,enabled,0.50
nike sneakers,phrase,800,30,15.75,90.00,2,enabled,0.45
athletic footwear,broad,1200,45,22.00,120.00,2,enabled,0.40
gym shoes,exact,500,10,5.00,25.00,1,enabled,0.35
sports shoes,phrase,600,15,8.00,40.00,1,enabled,0.38
EOF

print_success "Sample CSV file created: $SAMPLE_FILE"
echo ""

# Test 1: Upload file
echo "======================================================================"
echo "Test 1: Upload File"
echo "======================================================================"
print_info "Uploading CSV file..."

UPLOAD_RESPONSE=$(curl -s -X POST "${API_URL}/api/upload" \
    -F "file=@${SAMPLE_FILE}" \
    -F "profile_id=${PROFILE_ID}")

echo "$UPLOAD_RESPONSE" | jq '.' 2>/dev/null || echo "$UPLOAD_RESPONSE"

# Extract upload_id from response
UPLOAD_ID=$(echo "$UPLOAD_RESPONSE" | jq -r '.upload_id' 2>/dev/null)

if [ -z "$UPLOAD_ID" ] || [ "$UPLOAD_ID" = "null" ]; then
    print_error "Failed to extract upload_id from response"
    exit 1
fi

print_success "File uploaded successfully. Upload ID: $UPLOAD_ID"
echo ""

# Test 2: Preview uploaded file
echo "======================================================================"
echo "Test 2: Preview Uploaded File"
echo "======================================================================"
print_info "Getting file preview..."

PREVIEW_RESPONSE=$(curl -s "${API_URL}/api/upload/${UPLOAD_ID}/preview")
echo "$PREVIEW_RESPONSE" | jq '.' 2>/dev/null || echo "$PREVIEW_RESPONSE"

# Check for validation errors
VALIDATION_ERRORS=$(echo "$PREVIEW_RESPONSE" | jq -r '.validation_errors | length' 2>/dev/null)
if [ "$VALIDATION_ERRORS" != "0" ]; then
    print_error "Validation errors found in uploaded file"
    echo "$PREVIEW_RESPONSE" | jq '.validation_errors' 2>/dev/null
else
    print_success "File preview retrieved. No validation errors."
fi
echo ""

# Test 3: Import file
echo "======================================================================"
echo "Test 3: Import File"
echo "======================================================================"
print_info "Starting import job..."

IMPORT_RESPONSE=$(curl -s -X POST "${API_URL}/api/import" \
    -H "Content-Type: application/json" \
    -d "{
        \"upload_id\": \"${UPLOAD_ID}\",
        \"profile_id\": \"${PROFILE_ID}\"
    }")

echo "$IMPORT_RESPONSE" | jq '.' 2>/dev/null || echo "$IMPORT_RESPONSE"

# Extract job_id from response
JOB_ID=$(echo "$IMPORT_RESPONSE" | jq -r '.job_id' 2>/dev/null)

if [ -z "$JOB_ID" ] || [ "$JOB_ID" = "null" ]; then
    print_error "Failed to extract job_id from response"
    exit 1
fi

print_success "Import job started. Job ID: $JOB_ID"
echo ""

# Test 4: Check import status
echo "======================================================================"
echo "Test 4: Check Import Status"
echo "======================================================================"
print_info "Checking import job status..."

# Wait a moment for the job to start
sleep 2

for i in {1..10}; do
    STATUS_RESPONSE=$(curl -s "${API_URL}/api/import/status/${JOB_ID}")
    STATUS=$(echo "$STATUS_RESPONSE" | jq -r '.status' 2>/dev/null)

    echo "$STATUS_RESPONSE" | jq '.' 2>/dev/null || echo "$STATUS_RESPONSE"

    if [ "$STATUS" = "completed" ]; then
        print_success "Import job completed successfully!"

        ROWS_PROCESSED=$(echo "$STATUS_RESPONSE" | jq -r '.rows_processed' 2>/dev/null)
        ROWS_ADDED=$(echo "$STATUS_RESPONSE" | jq -r '.rows_added' 2>/dev/null)
        ROWS_SKIPPED=$(echo "$STATUS_RESPONSE" | jq -r '.rows_skipped' 2>/dev/null)

        echo ""
        echo "Import Summary:"
        echo "  - Rows Processed: $ROWS_PROCESSED"
        echo "  - Rows Added: $ROWS_ADDED"
        echo "  - Rows Skipped: $ROWS_SKIPPED"
        break
    elif [ "$STATUS" = "failed" ]; then
        print_error "Import job failed!"
        echo "$STATUS_RESPONSE" | jq '.errors' 2>/dev/null
        exit 1
    else
        print_info "Job status: $STATUS (attempt $i/10)"
        sleep 2
    fi
done

echo ""

# Test 5: Verify with invalid file type
echo "======================================================================"
echo "Test 5: Test Invalid File Type (Should Fail)"
echo "======================================================================"
print_info "Attempting to upload invalid file type..."

INVALID_FILE="data/uploads/test.txt"
echo "This is not a valid spreadsheet" > "$INVALID_FILE"

INVALID_RESPONSE=$(curl -s -X POST "${API_URL}/api/upload" \
    -F "file=@${INVALID_FILE}" \
    -F "profile_id=${PROFILE_ID}")

echo "$INVALID_RESPONSE" | jq '.' 2>/dev/null || echo "$INVALID_RESPONSE"

if echo "$INVALID_RESPONSE" | grep -q "Unsupported file type"; then
    print_success "Correctly rejected invalid file type"
else
    print_error "Failed to reject invalid file type"
fi
echo ""

# Cleanup
print_info "Cleaning up test files..."
rm -f "$SAMPLE_FILE"
rm -f "$INVALID_FILE"
print_success "Cleanup complete"

echo ""
echo "======================================================================"
echo "All Tests Completed!"
echo "======================================================================"
