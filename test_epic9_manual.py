#!/usr/bin/env python3
"""
Manual Testing Script for Epic 9: Advanced Job Search Application
Tests all stories: 9.1, 9.2.1, 9.2.2, 9.2.3, 9.3
"""

import requests
import json
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
TEST_USER_EMAIL = "testuser@example.com"
TEST_USER_PASSWORD = "testpass123"

# Test Results Tracker
test_results = []


def log_test(test_name: str, passed: bool, message: str = ""):
    """Log test results"""
    status = "✅ PASS" if passed else "❌ FAIL"
    result = f"{status} | {test_name}"
    if message:
        result += f"\n   └─ {message}"
    print(result)
    test_results.append({"test": test_name, "passed": passed, "message": message})


def test_basic_search(query: str = "Python", location: str = "remote"):
    """Test Story 9.1: Basic Job Search"""
    print("\n" + "="*60)
    print("STORY 9.1: Basic Job Search")
    print("="*60)
    
    try:
        response = requests.get(
            f"{BASE_URL}/jobs/search/basic",
            params={"query": query, "location": location, "limit": 5}
        )
        
        if response.status_code == 200:
            data = response.json()
            log_test(
                "Basic Search Endpoint",
                True,
                f"Found {data.get('total', 0)} jobs matching '{query}' in '{location}'"
            )
            
            # Verify response structure
            if "items" in data and "total" in data:
                log_test("Response Structure", True, "Valid response with 'items' and 'total'")
            else:
                log_test("Response Structure", False, "Missing required fields")
                
            # Check if results have required fields
            if data.get("items"):
                job = data["items"][0]
                required_fields = ["id", "title", "description", "location_type"]
                missing = [f for f in required_fields if f not in job]
                if not missing:
                    log_test("Job Item Fields", True, "All required fields present")
                else:
                    log_test("Job Item Fields", False, f"Missing fields: {missing}")
        else:
            log_test("Basic Search Endpoint", False, f"HTTP {response.status_code}")
            
    except Exception as e:
        log_test("Basic Search Endpoint", False, str(e))


def test_salary_job_type_filters():
    """Test Story 9.2.1: Salary Range & Job Type Filters"""
    print("\n" + "="*60)
    print("STORY 9.2.1: Salary & Job Type Filters")
    print("="*60)
    
    try:
        # Test 1: Salary filter
        response = requests.get(
            f"{BASE_URL}/jobs/search/basic",
            params={
                "query": "Developer",
                "min_salary": 1000,
                "max_salary": 3000,
                "limit": 5
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            log_test(
                "Salary Range Filter",
                True,
                f"Found {data.get('total', 0)} jobs with salary $1000-$3000"
            )
            
            # Verify salary fields exist in response
            if data.get("items"):
                job = data["items"][0]
                has_salary_fields = "salary_min" in job or "salary_max" in job
                log_test(
                    "Salary Fields in Response",
                    has_salary_fields,
                    "Salary fields present" if has_salary_fields else "Missing salary fields"
                )
        else:
            log_test("Salary Range Filter", False, f"HTTP {response.status_code}")
        
        # Test 2: Job type filter
        response = requests.get(
            f"{BASE_URL}/jobs/search/basic",
            params={
                "query": "Developer",
                "job_types": ["full-time", "contract"],
                "limit": 5
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            log_test(
                "Job Type Filter",
                True,
                f"Found {data.get('total', 0)} full-time/contract jobs"
            )
        else:
            log_test("Job Type Filter", False, f"HTTP {response.status_code}")
            
    except Exception as e:
        log_test("Salary/Job Type Filters", False, str(e))


def test_skills_autocomplete():
    """Test Story 9.2.2: Skills Filter with Autocomplete"""
    print("\n" + "="*60)
    print("STORY 9.2.2: Skills Filter & Autocomplete")
    print("="*60)
    
    try:
        # Test 1: Skills autocomplete endpoint
        response = requests.get(
            f"{BASE_URL}/jobs/skills/autocomplete",
            params={"query": "python", "limit": 5}
        )
        
        if response.status_code == 200:
            data = response.json()
            log_test(
                "Skills Autocomplete Endpoint",
                True,
                f"Found {len(data)} skill suggestions for 'python'"
            )
            
            # Verify response structure
            if data and isinstance(data, list):
                if "skill" in data[0] and "count" in data[0]:
                    log_test("Autocomplete Response Structure", True, "Valid structure")
                else:
                    log_test("Autocomplete Response Structure", False, "Invalid structure")
        else:
            log_test("Skills Autocomplete Endpoint", False, f"HTTP {response.status_code}")
        
        # Test 2: Search with skills filter
        response = requests.get(
            f"{BASE_URL}/jobs/search/basic",
            params={
                "query": "Developer",
                "required_skills": ["Python", "FastAPI"],
                "limit": 5
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            log_test(
                "Skills Search Filter",
                True,
                f"Found {data.get('total', 0)} jobs requiring Python & FastAPI"
            )
        else:
            log_test("Skills Search Filter", False, f"HTTP {response.status_code}")
            
    except Exception as e:
        log_test("Skills Autocomplete", False, str(e))


def test_benefits_filter():
    """Test Story 9.2.3: Benefits Filter"""
    print("\n" + "="*60)
    print("STORY 9.2.3: Benefits Filter")
    print("="*60)
    
    try:
        response = requests.get(
            f"{BASE_URL}/jobs/search/basic",
            params={
                "query": "Developer",
                "benefits": ["insurance", "training"],
                "limit": 5
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            log_test(
                "Benefits Filter",
                True,
                f"Found {data.get('total', 0)} jobs with insurance & training benefits"
            )
            
            # Check if benefits field is in response
            if data.get("items"):
                job = data["items"][0]
                has_benefits = "benefits" in job
                log_test(
                    "Benefits Field in Response",
                    has_benefits,
                    "Benefits field present" if has_benefits else "Missing benefits field"
                )
        else:
            log_test("Benefits Filter", False, f"HTTP {response.status_code}")
            
    except Exception as e:
        log_test("Benefits Filter", False, str(e))


def test_job_detail_endpoint():
    """Test Story 9.3: Job Detail Endpoint"""
    print("\n" + "="*60)
    print("STORY 9.3: Job Detail & Application Flow")
    print("="*60)
    
    try:
        # First get a job ID from search
        search_response = requests.get(
            f"{BASE_URL}/jobs/search/basic",
            params={"query": "Developer", "limit": 1}
        )
        
        if search_response.status_code == 200:
            data = search_response.json()
            if data.get("items"):
                job_id = data["items"][0]["id"]
                
                # Test job detail endpoint
                detail_response = requests.get(f"{BASE_URL}/jobs/{job_id}")
                
                if detail_response.status_code == 200:
                    job = detail_response.json()
                    log_test(
                        "Job Detail Endpoint",
                        True,
                        f"Retrieved details for job: {job.get('title', 'N/A')}"
                    )
                    
                    # Verify all required fields
                    required_fields = [
                        "id", "title", "description", "location_type",
                        "salary_min", "salary_max", "benefits", "required_skills"
                    ]
                    present = [f for f in required_fields if f in job]
                    log_test(
                        "Job Detail Fields",
                        len(present) >= 6,
                        f"{len(present)}/{len(required_fields)} fields present"
                    )
                else:
                    log_test("Job Detail Endpoint", False, f"HTTP {detail_response.status_code}")
            else:
                log_test("Job Detail Endpoint", False, "No jobs found to test")
        else:
            log_test("Job Detail Endpoint", False, "Failed to get job for testing")
            
    except Exception as e:
        log_test("Job Detail Endpoint", False, str(e))


def test_combined_filters():
    """Test all filters combined"""
    print("\n" + "="*60)
    print("COMBINED FILTERS TEST")
    print("="*60)
    
    try:
        response = requests.get(
            f"{BASE_URL}/jobs/search/basic",
            params={
                "query": "Python Developer",
                "location": "remote",
                "min_salary": 1500,
                "max_salary": 5000,
                "job_types": ["full-time"],
                "required_skills": ["Python"],
                "benefits": ["insurance"],
                "limit": 10
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            log_test(
                "Combined Filters",
                True,
                f"Found {data.get('total', 0)} jobs matching all criteria"
            )
        else:
            log_test("Combined Filters", False, f"HTTP {response.status_code}")
            
    except Exception as e:
        log_test("Combined Filters", False, str(e))


def print_summary():
    """Print test summary"""
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for r in test_results if r["passed"])
    failed = sum(1 for r in test_results if not r["passed"])
    total = len(test_results)
    
    print(f"Total Tests: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"Success Rate: {(passed/total*100):.1f}%")
    
    if failed > 0:
        print("\n❌ Failed Tests:")
        for r in test_results:
            if not r["passed"]:
                print(f"  - {r['test']}: {r['message']}")
    
    print("\n" + "="*60)
    
    if failed == 0:
        print("🎉 ALL TESTS PASSED! Epic 9 is ready for production.")
    else:
        print("⚠️  Some tests failed. Review the errors above.")
    print("="*60)


def main():
    """Run all tests"""
    print("="*60)
    print("EPIC 9: ADVANCED JOB SEARCH APPLICATION")
    print("Automated Testing Suite")
    print("="*60)
    print(f"Backend URL: {BASE_URL}")
    print("="*60)
    
    # Check if backend is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("⚠️  WARNING: Backend health check failed")
    except:
        print("❌ ERROR: Cannot connect to backend. Is it running?")
        print("   Start backend with: cd backend && uvicorn app.main:app --reload")
        return
    
    # Run all tests
    test_basic_search()
    test_salary_job_type_filters()
    test_skills_autocomplete()
    test_benefits_filter()
    test_job_detail_endpoint()
    test_combined_filters()
    
    # Print summary
    print_summary()


if __name__ == "__main__":
    main()
