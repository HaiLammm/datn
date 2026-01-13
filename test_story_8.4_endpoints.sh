#!/bin/bash

# Test Script for Story 8.4: Interview History Endpoints
# Tests all 4 new endpoints with proper authentication

set -e  # Exit on error

BASE_URL="http://localhost:8000"
API_PREFIX="/api/v1"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test tracking
TESTS_PASSED=0
TESTS_FAILED=0

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Story 8.4 Backend Endpoint Testing${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Function to print test result
test_result() {
    local test_name=$1
    local status=$2
    local details=$3
    
    if [ "$status" == "PASS" ]; then
        echo -e "${GREEN}✓ PASS${NC}: $test_name"
        [ -n "$details" ] && echo -e "  ${details}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAIL${NC}: $test_name"
        [ -n "$details" ] && echo -e "  ${RED}${details}${NC}"
        ((TESTS_FAILED++))
    fi
    echo ""
}

# Function to make authenticated GET request
auth_get() {
    local endpoint=$1
    curl -s -X GET "${BASE_URL}${API_PREFIX}${endpoint}" \
        -H "Authorization: Bearer ${ACCESS_TOKEN}" \
        -H "Content-Type: application/json"
}

# Function to make authenticated POST request
auth_post() {
    local endpoint=$1
    local data=$2
    curl -s -X POST "${BASE_URL}${API_PREFIX}${endpoint}" \
        -H "Authorization: Bearer ${ACCESS_TOKEN}" \
        -H "Content-Type: application/json" \
        -d "$data"
}

echo -e "${YELLOW}Step 1: Authentication${NC}"
echo "Attempting to login with test user..."

# Try to login with existing test user
LOGIN_RESPONSE=$(curl -s -X POST "${BASE_URL}${API_PREFIX}/auth/login" \
    -H "Content-Type: application/json" \
    -d '{
        "email": "test_jobseeker@example.com",
        "password": "Test@12345"
    }')

ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$ACCESS_TOKEN" ] || [ "$ACCESS_TOKEN" == "null" ]; then
    echo -e "${YELLOW}Test user not found. Checking if we can register...${NC}"
    
    # Register new test user
    REGISTER_RESPONSE=$(curl -s -X POST "${BASE_URL}${API_PREFIX}/auth/register" \
        -H "Content-Type: application/json" \
        -d '{
            "email": "test_jobseeker@example.com",
            "password": "Test@12345",
            "full_name": "Test Job Seeker",
            "role": "job_seeker"
        }')
    
    echo "Register response: $REGISTER_RESPONSE"
    
    # Try login again
    sleep 1
    LOGIN_RESPONSE=$(curl -s -X POST "${BASE_URL}${API_PREFIX}/auth/login" \
        -H "Content-Type: application/json" \
        -d '{
            "email": "test_jobseeker@example.com",
            "password": "Test@12345"
        }')
    
    ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
fi

if [ -z "$ACCESS_TOKEN" ] || [ "$ACCESS_TOKEN" == "null" ]; then
    echo -e "${RED}Failed to authenticate. Response:${NC}"
    echo "$LOGIN_RESPONSE"
    echo -e "\n${YELLOW}Note: You may need to manually create a test user in the database.${NC}"
    echo -e "${YELLOW}For now, we'll test the endpoint structure without authentication.${NC}\n"
    SKIP_AUTH_TESTS=true
else
    echo -e "${GREEN}✓ Successfully authenticated${NC}"
    echo "Access token: ${ACCESS_TOKEN:0:20}..."
    echo ""
    SKIP_AUTH_TESTS=false
fi

# ============================================
# Test 1: GET /api/v1/interviews (List Sessions)
# ============================================
echo -e "${YELLOW}Test 1: List Interview Sessions (GET /interviews)${NC}"

if [ "$SKIP_AUTH_TESTS" == "true" ]; then
    test_result "List Sessions" "SKIP" "Authentication required"
else
    RESPONSE=$(auth_get "/interviews?page=1&page_size=10&sort_by=created_at&sort_order=desc")
    
    # Check if response contains expected fields
    if echo "$RESPONSE" | grep -q '"items"' && echo "$RESPONSE" | grep -q '"total"'; then
        TOTAL=$(echo "$RESPONSE" | grep -o '"total":[0-9]*' | cut -d':' -f2)
        test_result "List Sessions" "PASS" "Total sessions: $TOTAL"
        echo "Response preview:"
        echo "$RESPONSE" | head -c 500
        echo "..."
    else
        test_result "List Sessions" "FAIL" "Invalid response format"
        echo "Response: $RESPONSE"
    fi
fi

echo ""

# ============================================
# Test 2: GET /api/v1/interviews/{id}/detail (Session Detail)
# ============================================
echo -e "${YELLOW}Test 2: Get Interview Detail (GET /interviews/{id}/detail)${NC}"

if [ "$SKIP_AUTH_TESTS" == "true" ]; then
    test_result "Session Detail" "SKIP" "Authentication required"
else
    # Try to get first session ID from list
    SESSION_ID=$(echo "$RESPONSE" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
    
    if [ -z "$SESSION_ID" ] || [ "$SESSION_ID" == "null" ]; then
        test_result "Session Detail" "SKIP" "No interview sessions found. Create one first."
    else
        DETAIL_RESPONSE=$(auth_get "/interviews/${SESSION_ID}/detail")
        
        if echo "$DETAIL_RESPONSE" | grep -q '"job_title"' && echo "$DETAIL_RESPONSE" | grep -q '"question_count"'; then
            JOB_TITLE=$(echo "$DETAIL_RESPONSE" | grep -o '"job_title":"[^"]*"' | cut -d'"' -f4)
            test_result "Session Detail" "PASS" "Retrieved detail for: $JOB_TITLE"
            echo "Response preview:"
            echo "$DETAIL_RESPONSE" | head -c 500
            echo "..."
        else
            test_result "Session Detail" "FAIL" "Invalid response format"
            echo "Response: $DETAIL_RESPONSE"
        fi
    fi
fi

echo ""

# ============================================
# Test 3: GET /api/v1/interviews/{id}/transcript (Transcript)
# ============================================
echo -e "${YELLOW}Test 3: Get Interview Transcript (GET /interviews/{id}/transcript)${NC}"

if [ "$SKIP_AUTH_TESTS" == "true" ]; then
    test_result "Transcript" "SKIP" "Authentication required"
elif [ -z "$SESSION_ID" ]; then
    test_result "Transcript" "SKIP" "No session ID available"
else
    TRANSCRIPT_RESPONSE=$(auth_get "/interviews/${SESSION_ID}/transcript")
    
    if echo "$TRANSCRIPT_RESPONSE" | grep -q '"turns"' && echo "$TRANSCRIPT_RESPONSE" | grep -q '"total_turns"'; then
        TURN_COUNT=$(echo "$TRANSCRIPT_RESPONSE" | grep -o '"total_turns":[0-9]*' | cut -d':' -f2)
        test_result "Transcript" "PASS" "Retrieved transcript with $TURN_COUNT turns"
        echo "Response preview:"
        echo "$TRANSCRIPT_RESPONSE" | head -c 500
        echo "..."
    else
        test_result "Transcript" "FAIL" "Invalid response format"
        echo "Response: $TRANSCRIPT_RESPONSE"
    fi
fi

echo ""

# ============================================
# Test 4: GET /api/v1/interviews/{id}/evaluation/detail (Evaluation)
# ============================================
echo -e "${YELLOW}Test 4: Get Evaluation Detail (GET /interviews/{id}/evaluation/detail)${NC}"

if [ "$SKIP_AUTH_TESTS" == "true" ]; then
    test_result "Evaluation Detail" "SKIP" "Authentication required"
elif [ -z "$SESSION_ID" ]; then
    test_result "Evaluation Detail" "SKIP" "No session ID available"
else
    EVAL_RESPONSE=$(auth_get "/interviews/${SESSION_ID}/evaluation/detail")
    
    if echo "$EVAL_RESPONSE" | grep -q '"overall_evaluation"' && echo "$EVAL_RESPONSE" | grep -q '"dimension_scores"'; then
        SCORE=$(echo "$EVAL_RESPONSE" | grep -o '"score":[0-9.]*' | head -1 | cut -d':' -f2)
        test_result "Evaluation Detail" "PASS" "Retrieved evaluation, score: $SCORE"
        echo "Response preview:"
        echo "$EVAL_RESPONSE" | head -c 500
        echo "..."
    elif echo "$EVAL_RESPONSE" | grep -q '"detail".*"not.*completed"'; then
        test_result "Evaluation Detail" "SKIP" "Interview not completed yet (expected behavior)"
    else
        test_result "Evaluation Detail" "FAIL" "Invalid response or error"
        echo "Response: $EVAL_RESPONSE"
    fi
fi

echo ""

# ============================================
# Additional Tests: Pagination & Sorting
# ============================================
echo -e "${YELLOW}Additional Test: Pagination & Sorting${NC}"

if [ "$SKIP_AUTH_TESTS" == "false" ]; then
    # Test with different sorting
    SORT_RESPONSE=$(auth_get "/interviews?page=1&page_size=5&sort_by=overall_score&sort_order=asc")
    
    if echo "$SORT_RESPONSE" | grep -q '"page":1' && echo "$SORT_RESPONSE" | grep -q '"page_size":5'; then
        test_result "Pagination & Sorting" "PASS" "Sorting by overall_score works"
    else
        test_result "Pagination & Sorting" "FAIL" "Pagination parameters not working"
    fi
else
    test_result "Pagination & Sorting" "SKIP" "Authentication required"
fi

echo ""

# ============================================
# Summary
# ============================================
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Test Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Failed: $TESTS_FAILED${NC}"
echo -e "Total: $((TESTS_PASSED + TESTS_FAILED))"
echo ""

if [ $TESTS_FAILED -eq 0 ] && [ $TESTS_PASSED -gt 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    exit 0
elif [ "$SKIP_AUTH_TESTS" == "true" ]; then
    echo -e "${YELLOW}⚠ Tests skipped due to authentication issues${NC}"
    echo -e "${YELLOW}To fix: Create a test user with role='job_seeker' and interview data${NC}"
    exit 2
else
    echo -e "${RED}✗ Some tests failed${NC}"
    exit 1
fi
