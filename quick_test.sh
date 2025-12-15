#!/bin/bash
# Quick Test Script for Amazon PPC Optimization Tool
# This script runs a series of quick tests to verify the implementation

set -e  # Exit on error

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   Amazon PPC - Quick Test Suite${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Change to project directory
cd "$(dirname "$0")"

# Test 1: Check Python version
echo -e "${BLUE}Test 1: Checking Python version...${NC}"
python3 --version
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Python 3 is installed${NC}"
else
    echo -e "${RED}✗ Python 3 not found${NC}"
    exit 1
fi
echo ""

# Test 2: Check .env file
echo -e "${BLUE}Test 2: Checking .env file...${NC}"
if [ -f ".env" ]; then
    echo -e "${GREEN}✓ .env file exists${NC}"
else
    echo -e "${RED}✗ .env file not found${NC}"
    exit 1
fi
echo ""

# Test 3: Verify environment
echo -e "${BLUE}Test 3: Verifying environment configuration...${NC}"
python3 verify_env.py
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Environment verified${NC}"
else
    echo -e "${YELLOW}⚠ Environment has some issues (see above)${NC}"
    echo -e "${YELLOW}  This may be OK - some features may not be configured yet${NC}"
fi
echo ""

# Test 4: Run automated tests
echo -e "${BLUE}Test 4: Running automated test suite...${NC}"
python3 run_tests.py
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ All automated tests passed${NC}"
else
    echo -e "${RED}✗ Some automated tests failed${NC}"
    exit 1
fi
echo ""

# Test 5: Test configuration command
echo -e "${BLUE}Test 5: Testing configuration command...${NC}"
python3 -m agent config > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Configuration command works${NC}"
else
    echo -e "${RED}✗ Configuration command failed${NC}"
    exit 1
fi
echo ""

# Test 6: Test health check
echo -e "${BLUE}Test 6: Testing health check command...${NC}"
python3 -m agent healthcheck > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Health check command works${NC}"
else
    echo -e "${RED}✗ Health check command failed${NC}"
    exit 1
fi
echo ""

# Summary
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✅ ALL QUICK TESTS PASSED!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${GREEN}Your implementation is working correctly.${NC}"
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo "  1. Start API server:"
echo "     ${YELLOW}python3 -m agent api${NC}"
echo ""
echo "  2. In another terminal, test the API:"
echo "     ${YELLOW}curl http://localhost:8000/health${NC}"
echo ""
echo "  3. Open API documentation:"
echo "     ${YELLOW}http://localhost:8000/docs${NC}"
echo ""
echo "  4. For detailed testing, see:"
echo "     ${YELLOW}TESTING_GUIDE.md${NC}"
echo ""
