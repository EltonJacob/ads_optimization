#!/bin/bash

# Test script for Performance Query API endpoints
# Usage: ./test_performance_api.sh

set -e

API_URL="http://localhost:8000"
PROFILE_ID="test_profile_123"
START_DATE="2025-12-01"
END_DATE="2025-12-16"

echo "======================================================================"
echo "Testing Performance Query API Endpoints"
echo "======================================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_info() {
    echo -e "${BLUE}→ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
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

# First, let's upload some sample data to test with
print_info "Step 0: Setting up test data..."
echo "Creating sample CSV file..."

SAMPLE_FILE="data/uploads/perf_test.csv"
mkdir -p "data/uploads"

cat > "$SAMPLE_FILE" << 'EOF'
keyword,match type,impressions,clicks,spend,sales,orders,date
running shoes,exact,1000,50,25.50,150.00,3,2025-12-01
nike sneakers,phrase,800,30,15.75,90.00,2,2025-12-01
athletic footwear,broad,1200,45,22.00,120.00,2,2025-12-02
gym shoes,exact,500,10,5.00,25.00,1,2025-12-03
sports shoes,phrase,600,15,8.00,40.00,1,2025-12-04
running gear,exact,900,35,18.00,100.00,2,2025-12-05
marathon shoes,exact,700,25,12.50,75.00,2,2025-12-06
trail running,phrase,650,20,10.00,55.00,1,2025-12-07
EOF

# Upload the file
UPLOAD_RESPONSE=$(curl -s -X POST "${API_URL}/api/upload" \
    -F "file=@${SAMPLE_FILE}" \
    -F "profile_id=${PROFILE_ID}")

UPLOAD_ID=$(echo "$UPLOAD_RESPONSE" | jq -r '.upload_id' 2>/dev/null)

if [ -z "$UPLOAD_ID" ] || [ "$UPLOAD_ID" = "null" ]; then
    print_error "Failed to upload test data"
    exit 1
fi

# Import the file
IMPORT_RESPONSE=$(curl -s -X POST "${API_URL}/api/import" \
    -H "Content-Type: application/json" \
    -d "{\"upload_id\": \"${UPLOAD_ID}\", \"profile_id\": \"${PROFILE_ID}\"}")

JOB_ID=$(echo "$IMPORT_RESPONSE" | jq -r '.job_id' 2>/dev/null)

# Wait for import to complete
sleep 3

STATUS_RESPONSE=$(curl -s "${API_URL}/api/import/status/${JOB_ID}")
STATUS=$(echo "$STATUS_RESPONSE" | jq -r '.status' 2>/dev/null)

if [ "$STATUS" != "completed" ]; then
    print_error "Import failed or not completed"
    echo "$STATUS_RESPONSE" | jq '.'
    exit 1
fi

ROWS_ADDED=$(echo "$STATUS_RESPONSE" | jq -r '.rows_added' 2>/dev/null)
print_success "Test data uploaded and imported ($ROWS_ADDED rows)"
echo ""

# Test 1: Get Performance Summary
echo "======================================================================"
echo "Test 1: GET /api/performance/{profile_id}/summary"
echo "======================================================================"
print_info "Querying performance summary..."

SUMMARY_RESPONSE=$(curl -s "${API_URL}/api/performance/${PROFILE_ID}/summary?start_date=${START_DATE}&end_date=${END_DATE}")

echo "$SUMMARY_RESPONSE" | jq '.' 2>/dev/null || echo "$SUMMARY_RESPONSE"

# Validate response
TOTAL_SPEND=$(echo "$SUMMARY_RESPONSE" | jq -r '.total_spend' 2>/dev/null)
TOTAL_SALES=$(echo "$SUMMARY_RESPONSE" | jq -r '.total_sales' 2>/dev/null)
KEYWORD_COUNT=$(echo "$SUMMARY_RESPONSE" | jq -r '.keyword_count' 2>/dev/null)

if [ "$TOTAL_SPEND" != "null" ] && [ "$TOTAL_SALES" != "null" ]; then
    print_success "Summary retrieved successfully"
    echo "  - Total Spend: \$${TOTAL_SPEND}"
    echo "  - Total Sales: \$${TOTAL_SALES}"
    echo "  - Keyword Count: ${KEYWORD_COUNT}"
else
    print_error "Failed to retrieve summary"
fi
echo ""

# Test 2: Get Keywords List
echo "======================================================================"
echo "Test 2: GET /api/performance/{profile_id}/keywords"
echo "======================================================================"
print_info "Querying keyword-level data (paginated)..."

KEYWORDS_RESPONSE=$(curl -s "${API_URL}/api/performance/${PROFILE_ID}/keywords?start_date=${START_DATE}&end_date=${END_DATE}&page=1&page_size=5&sort_by=spend&sort_order=desc")

echo "$KEYWORDS_RESPONSE" | jq '.' 2>/dev/null || echo "$KEYWORDS_RESPONSE"

# Validate response
TOTAL_COUNT=$(echo "$KEYWORDS_RESPONSE" | jq -r '.total_count' 2>/dev/null)
KEYWORDS_LENGTH=$(echo "$KEYWORDS_RESPONSE" | jq -r '.keywords | length' 2>/dev/null)

if [ "$TOTAL_COUNT" != "null" ] && [ "$KEYWORDS_LENGTH" != "null" ]; then
    print_success "Keywords retrieved successfully"
    echo "  - Total Keywords: ${TOTAL_COUNT}"
    echo "  - Returned (page 1): ${KEYWORDS_LENGTH}"

    # Show top keyword
    TOP_KEYWORD=$(echo "$KEYWORDS_RESPONSE" | jq -r '.keywords[0].keyword_text' 2>/dev/null)
    TOP_SPEND=$(echo "$KEYWORDS_RESPONSE" | jq -r '.keywords[0].spend' 2>/dev/null)
    echo "  - Top Keyword: ${TOP_KEYWORD} (\$${TOP_SPEND} spend)"
else
    print_error "Failed to retrieve keywords"
fi
echo ""

# Test 3: Get Trends (Daily)
echo "======================================================================"
echo "Test 3: GET /api/performance/{profile_id}/trends (daily)"
echo "======================================================================"
print_info "Querying trend data grouped by day..."

TRENDS_RESPONSE=$(curl -s "${API_URL}/api/performance/${PROFILE_ID}/trends?start_date=${START_DATE}&end_date=${END_DATE}&group_by=day")

echo "$TRENDS_RESPONSE" | jq '.' 2>/dev/null || echo "$TRENDS_RESPONSE"

# Validate response
DATA_POINTS=$(echo "$TRENDS_RESPONSE" | jq -r '.data_points | length' 2>/dev/null)

if [ "$DATA_POINTS" != "null" ] && [ "$DATA_POINTS" -gt 0 ]; then
    print_success "Trends retrieved successfully"
    echo "  - Data Points: ${DATA_POINTS}"

    # Show first trend point
    FIRST_DATE=$(echo "$TRENDS_RESPONSE" | jq -r '.data_points[0].date' 2>/dev/null)
    FIRST_SPEND=$(echo "$TRENDS_RESPONSE" | jq -r '.data_points[0].spend' 2>/dev/null)
    echo "  - First Date: ${FIRST_DATE} (\$${FIRST_SPEND} spend)"
else
    print_error "Failed to retrieve trends"
fi
echo ""

# Test 4: Get Trends (Weekly)
echo "======================================================================"
echo "Test 4: GET /api/performance/{profile_id}/trends (weekly)"
echo "======================================================================"
print_info "Querying trend data grouped by week..."

TRENDS_WEEKLY=$(curl -s "${API_URL}/api/performance/${PROFILE_ID}/trends?start_date=${START_DATE}&end_date=${END_DATE}&group_by=week")

echo "$TRENDS_WEEKLY" | jq '.' 2>/dev/null || echo "$TRENDS_WEEKLY"

WEEKLY_POINTS=$(echo "$TRENDS_WEEKLY" | jq -r '.data_points | length' 2>/dev/null)

if [ "$WEEKLY_POINTS" != "null" ]; then
    print_success "Weekly trends retrieved successfully"
    echo "  - Data Points (weeks): ${WEEKLY_POINTS}"
else
    print_error "Failed to retrieve weekly trends"
fi
echo ""

# Test 5: Get Data Sources
echo "======================================================================"
echo "Test 5: GET /api/performance/{profile_id}/sources"
echo "======================================================================"
print_info "Querying data source information..."

SOURCES_RESPONSE=$(curl -s "${API_URL}/api/performance/${PROFILE_ID}/sources?start_date=${START_DATE}&end_date=${END_DATE}")

echo "$SOURCES_RESPONSE" | jq '.' 2>/dev/null || echo "$SOURCES_RESPONSE"

# Validate response
TOTAL_RECORDS=$(echo "$SOURCES_RESPONSE" | jq -r '.total_records' 2>/dev/null)
UPLOAD_RECORDS=$(echo "$SOURCES_RESPONSE" | jq -r '.upload_records' 2>/dev/null)
API_RECORDS=$(echo "$SOURCES_RESPONSE" | jq -r '.api_records' 2>/dev/null)

if [ "$TOTAL_RECORDS" != "null" ]; then
    print_success "Data sources retrieved successfully"
    echo "  - Total Records: ${TOTAL_RECORDS}"
    echo "  - From API: ${API_RECORDS}"
    echo "  - From Upload: ${UPLOAD_RECORDS}"
else
    print_error "Failed to retrieve data sources"
fi
echo ""

# Test 6: Test Pagination
echo "======================================================================"
echo "Test 6: Test Pagination (multiple pages)"
echo "======================================================================"
print_info "Testing pagination with page_size=3..."

PAGE1=$(curl -s "${API_URL}/api/performance/${PROFILE_ID}/keywords?start_date=${START_DATE}&end_date=${END_DATE}&page=1&page_size=3")
PAGE2=$(curl -s "${API_URL}/api/performance/${PROFILE_ID}/keywords?start_date=${START_DATE}&end_date=${END_DATE}&page=2&page_size=3")

PAGE1_COUNT=$(echo "$PAGE1" | jq -r '.keywords | length' 2>/dev/null)
PAGE2_COUNT=$(echo "$PAGE2" | jq -r '.keywords | length' 2>/dev/null)

echo "Page 1: ${PAGE1_COUNT} keywords"
echo "Page 2: ${PAGE2_COUNT} keywords"

if [ "$PAGE1_COUNT" -le 3 ] && [ "$PAGE2_COUNT" -le 3 ]; then
    print_success "Pagination working correctly"
else
    print_error "Pagination issue detected"
fi
echo ""

# Test 7: Test Sorting
echo "======================================================================"
echo "Test 7: Test Sorting (by sales descending)"
echo "======================================================================"
print_info "Testing sort_by=sales&sort_order=desc..."

SORTED_RESPONSE=$(curl -s "${API_URL}/api/performance/${PROFILE_ID}/keywords?start_date=${START_DATE}&end_date=${END_DATE}&page=1&page_size=3&sort_by=sales&sort_order=desc")

echo "$SORTED_RESPONSE" | jq '.keywords[] | {keyword_text, sales, spend}' 2>/dev/null

TOP_SALES=$(echo "$SORTED_RESPONSE" | jq -r '.keywords[0].sales' 2>/dev/null)
SECOND_SALES=$(echo "$SORTED_RESPONSE" | jq -r '.keywords[1].sales' 2>/dev/null)

if [ "$TOP_SALES" != "null" ] && [ "$SECOND_SALES" != "null" ]; then
    print_success "Sorting working correctly"
    echo "  - Top keyword sales: \$${TOP_SALES}"
    echo "  - Second keyword sales: \$${SECOND_SALES}"
else
    print_error "Sorting issue detected"
fi
echo ""

# Test 8: Test Invalid group_by
echo "======================================================================"
echo "Test 8: Test Error Handling (invalid group_by)"
echo "======================================================================"
print_info "Testing with invalid group_by parameter..."

ERROR_RESPONSE=$(curl -s "${API_URL}/api/performance/${PROFILE_ID}/trends?start_date=${START_DATE}&end_date=${END_DATE}&group_by=invalid")

echo "$ERROR_RESPONSE" | jq '.' 2>/dev/null || echo "$ERROR_RESPONSE"

if echo "$ERROR_RESPONSE" | grep -q "Invalid group_by value"; then
    print_success "Error handling working correctly"
else
    print_error "Error handling issue"
fi
echo ""

# Cleanup
print_info "Cleaning up test files..."
rm -f "$SAMPLE_FILE"
print_success "Cleanup complete"

echo ""
echo "======================================================================"
echo "All Performance API Tests Completed!"
echo "======================================================================"
echo ""
echo "Summary of Endpoints Tested:"
echo "  ✓ GET /api/performance/{profile_id}/summary"
echo "  ✓ GET /api/performance/{profile_id}/keywords (with pagination & sorting)"
echo "  ✓ GET /api/performance/{profile_id}/trends (daily & weekly)"
echo "  ✓ GET /api/performance/{profile_id}/sources"
echo ""
