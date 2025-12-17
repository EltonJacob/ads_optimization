#!/bin/bash
# Test script for Amazon Ads API integration

set -e

echo "================================"
echo "Amazon Ads API Integration Test"
echo "================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

BASE_URL="http://localhost:8000"

echo -e "${YELLOW}1. Testing API Health Check...${NC}"
curl -s "$BASE_URL/api/health" | jq '.'
echo ""

echo -e "${YELLOW}2. Triggering Amazon Ads API Fetch...${NC}"
echo "   Requesting keyword report for last 7 days"

# Calculate dates
END_DATE=$(date +%Y-%m-%d)
START_DATE=$(date -v-7d +%Y-%m-%d 2>/dev/null || date -d '7 days ago' +%Y-%m-%d)

# Get profile ID from .env or use default
PROFILE_ID="${AMAZON_ADS_PROFILE_ID:-3615809640282046}"

echo "   Start Date: $START_DATE"
echo "   End Date: $END_DATE"
echo "   Profile ID: $PROFILE_ID"
echo ""

# Trigger fetch
FETCH_RESPONSE=$(curl -s -X POST "$BASE_URL/api/fetch" \
  -H "Content-Type: application/json" \
  -d "{
    \"profile_id\": \"$PROFILE_ID\",
    \"start_date\": \"$START_DATE\",
    \"end_date\": \"$END_DATE\",
    \"report_type\": \"KEYWORDS\"
  }")

echo "$FETCH_RESPONSE" | jq '.'
JOB_ID=$(echo "$FETCH_RESPONSE" | jq -r '.job_id')

if [ "$JOB_ID" = "null" ] || [ -z "$JOB_ID" ]; then
    echo -e "${RED}❌ Failed to get job ID${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✓ Fetch job started: $JOB_ID${NC}"
echo ""

echo -e "${YELLOW}3. Polling Job Status...${NC}"
echo "   This will take a few minutes as Amazon generates the report"
echo ""

MAX_ATTEMPTS=60
ATTEMPT=0
SLEEP_INTERVAL=10

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    ATTEMPT=$((ATTEMPT + 1))

    STATUS_RESPONSE=$(curl -s "$BASE_URL/api/fetch/status/$JOB_ID")
    STATUS=$(echo "$STATUS_RESPONSE" | jq -r '.status')
    PROGRESS=$(echo "$STATUS_RESPONSE" | jq -r '.progress // 0')
    RECORDS=$(echo "$STATUS_RESPONSE" | jq -r '.records_fetched // 0')

    echo "   Attempt $ATTEMPT/$MAX_ATTEMPTS: Status=$STATUS, Progress=$PROGRESS%, Records=$RECORDS"

    if [ "$STATUS" = "completed" ]; then
        echo ""
        echo -e "${GREEN}✓ Job completed successfully!${NC}"
        echo "$STATUS_RESPONSE" | jq '.'
        break
    elif [ "$STATUS" = "failed" ] || [ "$STATUS" = "timeout" ]; then
        echo ""
        echo -e "${RED}❌ Job failed or timed out${NC}"
        echo "$STATUS_RESPONSE" | jq '.'
        exit 1
    fi

    sleep $SLEEP_INTERVAL
done

if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
    echo ""
    echo -e "${RED}❌ Polling timed out after $MAX_ATTEMPTS attempts${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}4. Verifying Data in Database...${NC}"

# Query performance summary to verify data was stored
SUMMARY_RESPONSE=$(curl -s "$BASE_URL/api/performance/$PROFILE_ID/summary?start_date=$START_DATE&end_date=$END_DATE")
KEYWORD_COUNT=$(echo "$SUMMARY_RESPONSE" | jq -r '.keyword_count // 0')

echo "   Total Keywords: $KEYWORD_COUNT"
echo ""

if [ "$KEYWORD_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✓ Data successfully stored in database!${NC}"
    echo ""
    echo "Performance Summary:"
    echo "$SUMMARY_RESPONSE" | jq '.'
else
    echo -e "${YELLOW}⚠ No keywords found in database${NC}"
    echo "   This might be normal if there's no data for the selected date range"
fi

echo ""
echo "================================"
echo -e "${GREEN}✓ Amazon Ads API Integration Test Complete${NC}"
echo "================================"
