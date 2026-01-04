#!/bin/bash

# API Testing Script for Database Expansion
# Tests all API endpoints with new sections and cases

echo "=========================================="
echo "API ENDPOINT TESTING"
echo "=========================================="

# Base URL - adjust if needed
BASE_URL="http://localhost:8000"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
PASSED=0
FAILED=0

# Function to test endpoint
test_endpoint() {
    local name="$1"
    local url="$2"
    local expected_status="${3:-200}"
    local search_term="$4"

    echo ""
    echo "Testing: $name"
    echo "URL: $url"

    response=$(curl -s -w "\n%{http_code}" "$url")
    status_code=$(echo "$response" | tail -n 1)
    body=$(echo "$response" | head -n -1)

    if [ "$status_code" -eq "$expected_status" ]; then
        if [ -n "$search_term" ]; then
            if echo "$body" | grep -q "$search_term"; then
                echo -e "${GREEN}✓ PASSED${NC} (Status: $status_code, Found: $search_term)"
                ((PASSED++))
            else
                echo -e "${RED}✗ FAILED${NC} (Status: $status_code, Missing: $search_term)"
                ((FAILED++))
            fi
        else
            echo -e "${GREEN}✓ PASSED${NC} (Status: $status_code)"
            ((PASSED++))
        fi
    else
        echo -e "${RED}✗ FAILED${NC} (Expected: $expected_status, Got: $status_code)"
        ((FAILED++))
    fi
}

echo ""
echo "Note: Make sure the backend server is running on $BASE_URL"
echo ""
read -p "Press Enter to start testing..."

echo ""
echo "=========================================="
echo "TEST 1: Health Check"
echo "=========================================="
test_endpoint "Health Check" "$BASE_URL/health"

echo ""
echo "=========================================="
echo "TEST 2: New IPC Sections"
echo "=========================================="

# Test new sections
test_endpoint "IPC 307 (Attempt to murder)" "$BASE_URL/api/ipc-bns/section/307" 200 "Attempt to murder"
test_endpoint "IPC 377 (Unnatural offences - repealed)" "$BASE_URL/api/ipc-bns/section/377" 200 "377"
test_endpoint "IPC 295A (Religious offences)" "$BASE_URL/api/ipc-bns/section/295A" 200 "religious"
test_endpoint "IPC 498A (Cruelty)" "$BASE_URL/api/ipc-bns/section/498A" 200 "498A"

echo ""
echo "=========================================="
echo "TEST 3: Section Search"
echo "=========================================="

test_endpoint "Search: kidnapping" "$BASE_URL/api/ipc-bns/search?query=kidnapping" 200 "363"
test_endpoint "Search: forgery" "$BASE_URL/api/ipc-bns/search?query=forgery" 200 "463"
test_endpoint "Search: abetment" "$BASE_URL/api/ipc-bns/search?query=abetment" 200 "107"

echo ""
echo "=========================================="
echo "TEST 4: Landmark Cases"
echo "=========================================="

# Test case search
test_endpoint "Case: Navtej Singh Johar" "$BASE_URL/api/cases/search?query=Navtej+Singh+Johar" 200 "Navtej"
test_endpoint "Case: D.K. Basu" "$BASE_URL/api/cases/search?query=D.K.+Basu" 200 "D.K. Basu"
test_endpoint "Case: Bachan Singh" "$BASE_URL/api/cases/search?query=Bachan+Singh" 200 "death penalty"

echo ""
echo "=========================================="
echo "TEST 5: Case Search by Section"
echo "=========================================="

test_endpoint "Cases for Section 377" "$BASE_URL/api/cases/by-section/377" 200 "377"
test_endpoint "Cases for Section 302" "$BASE_URL/api/cases/by-section/302" 200 "murder"
test_endpoint "Cases for Section 307" "$BASE_URL/api/cases/by-section/307" 200 "307"

echo ""
echo "=========================================="
echo "TEST 6: All Sections Endpoint"
echo "=========================================="

test_endpoint "Get all sections" "$BASE_URL/api/ipc-bns/sections" 200

echo ""
echo "=========================================="
echo "TEST 7: All Cases Endpoint"
echo "=========================================="

test_endpoint "Get all cases" "$BASE_URL/api/cases" 200

echo ""
echo "=========================================="
echo "TEST SUMMARY"
echo "=========================================="
echo -e "Passed: ${GREEN}$PASSED${NC}"
echo -e "Failed: ${RED}$FAILED${NC}"
echo "Total: $((PASSED + FAILED))"

if [ $FAILED -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 ALL API TESTS PASSED!${NC}"
    exit 0
else
    echo ""
    echo -e "${YELLOW}⚠️  Some tests failed. Check the output above.${NC}"
    exit 1
fi
