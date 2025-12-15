#!/bin/bash

echo "Testing Data Fetch API Endpoints"
echo "================================="
echo ""

# Test 1: Health check
echo "1. Testing health check endpoint..."
curl -s "http://localhost:8000/api/health" | python3 -m json.tool
echo ""
echo ""

# Test 2: Trigger a fetch job (30 days)
echo "2. Triggering fetch job (30 days)..."
RESPONSE=$(curl -s -X POST "http://localhost:8000/api/fetch" \
  -H "Content-Type: application/json" \
  -d '{"profile_id":"12345678","start_date":"2025-11-01","end_date":"2025-11-30","report_type":"KEYWORDS"}')

echo "$RESPONSE" | python3 -m json.tool
JOB_ID=$(echo "$RESPONSE" | python3 -c "import json,sys; print(json.load(sys.stdin)['job_id'])")
echo ""
echo "Job ID: $JOB_ID"
echo ""

# Test 3: Check status immediately
echo "3. Checking status immediately..."
curl -s "http://localhost:8000/api/fetch/status/$JOB_ID" | python3 -m json.tool
echo ""
echo ""

# Test 4: Check status after 3 seconds
echo "4. Waiting 3 seconds..."
sleep 3
echo "Checking status after 3 seconds..."
curl -s "http://localhost:8000/api/fetch/status/$JOB_ID" | python3 -m json.tool
echo ""
echo ""

# Test 5: Check final status
echo "5. Waiting 10 more seconds for completion..."
sleep 10
echo "Final status:"
curl -s "http://localhost:8000/api/fetch/status/$JOB_ID" | python3 -m json.tool
echo ""
echo ""

# Test 6: Test with invalid job ID
echo "6. Testing with invalid job ID..."
curl -s "http://localhost:8000/api/fetch/status/invalid_job_123" | python3 -m json.tool
echo ""
echo ""

echo "✅ All tests completed!"
