#!/bin/bash

# Test script for job match fix
echo "=== Job Match Fix Test ==="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test data
JD_ID="68dacfcc-0c9c-4e8d-a7ad-93404182ffaa"
CV_ID="4152d60c-c654-4b20-8415-09a1dadea36b"
RECRUITER_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJyZWNydWl0ZXJAZXhhbXBsZS5jb20iLCJyb2xlIjoicmVjcnVpdGVyIiwiZXhwIjoxNzY4MzIxODY0LCJ0eXBlIjoiYWNjZXNzIn0.ezccqojcSfG-o8epOg7YsZnh6YBPHglVa6ljgUxmvAM"
JOBSEEKER_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2JzZWVrZXJAZXhhbXBsZS5jb20iLCJyb2xlIjoiam9iX3NlZWtlciIsImV4cCI6MTc2ODMyMTg4NiwidHlwZSI6ImFjY2VzcyJ9.pPawC1h_Mx0D83tSMsrSRSav7pYYdA30jmBaiNYo-cM"

echo -e "${YELLOW}1. Testing direct backend API (recruiter)${NC}"
echo -e "Expected: 200 OK with job match score"
response=$(curl -s -w "HTTP %{http_code}" -X POST "http://localhost:8000/api/v1/jobs/jd/$JD_ID/match" \
  -H "Authorization: Bearer $RECRUITER_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"cv_id\": \"$CV_ID\"}")
echo "$response"
echo ""

echo -e "${YELLOW}2. Testing direct backend API (job_seeker)${NC}"
echo -e "Expected: 403 Forbidden"
response=$(curl -s -w "HTTP %{http_code}" -X POST "http://localhost:8000/api/v1/jobs/jd/$JD_ID/match" \
  -H "Authorization: Bearer $JOBSEEKER_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"cv_id\": \"$CV_ID\"}")
echo "$response"
echo ""

echo -e "${YELLOW}3. Testing Next.js API route (recruiter)${NC}"
echo -e "Expected: 200 OK with job match score"
response=$(curl -s -w "HTTP %{http_code}" -X POST "http://localhost:3000/api/jobs/jd/$JD_ID/match" \
  -H "Cookie: access_token=$RECRUITER_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"cv_id\": \"$CV_ID\"}")
echo "$response"
echo ""

echo -e "${YELLOW}4. Testing Next.js API route (job_seeker)${NC}"
echo -e "Expected: 403 Forbidden"
response=$(curl -s -w "HTTP %{http_code}" -X POST "http://localhost:3000/api/jobs/jd/$JD_ID/match" \
  -H "Cookie: access_token=$JOBSEEKER_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"cv_id\": \"$CV_ID\"}")
echo "$response"
echo ""

echo -e "${YELLOW}5. Testing Next.js API route (no auth)${NC}"
echo -e "Expected: 401 Unauthorized"
response=$(curl -s -w "HTTP %{http_code}" -X POST "http://localhost:3000/api/jobs/jd/$JD_ID/match" \
  -H "Content-Type: application/json" \
  -d "{\"cv_id\": \"$CV_ID\"}")
echo "$response"
echo ""

echo -e "${GREEN}Test completed!${NC}"
echo -e "${GREEN}The fix should resolve the 403 error when client components${NC}"
echo -e "${GREEN}call the job match API by using the Next.js API route proxy.${NC}"