#!/usr/bin/env python3
"""
Test script to debug experience scoring bug
Upload 2 CVs and compare their experience scores
"""
import requests
import time
from pathlib import Path

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "password123"

# CV files to test
CV_21_YEARS = Path("data-cv/15.pdf")  # 21+ years experience
CV_3_YEARS = Path("data-cv/Lam-Luong-Hai-TopCV.vn-131225.21323.pdf")  # 3 years experience

# Session and auth token
session = requests.Session()
auth_token = None


def login():
    """Login and get access token"""
    global auth_token
    print("🔐 Logging in...")
    
    response = session.post(
        f"{API_BASE_URL}/auth/login",
        json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        auth_token = data.get('access_token')
        session.headers.update({'Authorization': f'Bearer {auth_token}'})
        print("✅ Login successful")
        return True
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(f"Response: {response.text}")
        return False


def upload_cv(cv_path: Path):
    """Upload a CV and return the CV ID"""
    if not cv_path.exists():
        print(f"❌ CV file not found: {cv_path}")
        return None
    
    print(f"\n📤 Uploading CV: {cv_path.name}")
    
    with open(cv_path, 'rb') as f:
        files = {
            'file': (cv_path.name, f, 'application/pdf')
        }
        
        response = session.post(
            f"{API_BASE_URL}/cvs/",
            files=files
        )
    
    if response.status_code == 201:
        cv_data = response.json()
        cv_id = cv_data['id']
        print(f"✅ CV uploaded successfully - ID: {cv_id}")
        return cv_id
    else:
        print(f"❌ Upload failed: {response.status_code}")
        print(f"Response: {response.text}")
        return None


def wait_for_analysis(cv_id, max_wait=180):
    """Wait for CV analysis to complete"""
    print(f"⏳ Waiting for analysis to complete (max {max_wait}s)...")
    
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        response = session.get(
            f"{API_BASE_URL}/ai/cvs/{cv_id}/status"
        )
        
        if response.status_code == 200:
            status_data = response.json()
            status = status_data.get('status')
            
            print(f"  Status: {status}", end='\r')
            
            if status == 'COMPLETED':
                print(f"\n✅ Analysis completed in {time.time() - start_time:.1f}s")
                return True
            elif status == 'FAILED':
                print(f"\n❌ Analysis failed")
                return False
        
        time.sleep(2)
    
    print(f"\n⏰ Timeout after {max_wait}s")
    return False


def get_analysis_results(cv_id):
    """Get analysis results for a CV"""
    print(f"\n📊 Fetching analysis results...")
    
    response = session.get(
        f"{API_BASE_URL}/ai/cvs/{cv_id}/analysis"
    )
    
    if response.status_code == 200:
        analysis = response.json()
        
        # Extract key metrics
        overall_score = analysis.get('ai_score', 'N/A')
        feedback = analysis.get('ai_feedback', {})
        criteria = feedback.get('criteria', {})
        exp_breakdown = feedback.get('experience_breakdown', {})
        
        experience_score = criteria.get('experience', 'N/A')
        total_years = exp_breakdown.get('total_years', 'N/A')
        
        print(f"  Overall Score: {overall_score}")
        print(f"  Experience Score: {experience_score}")
        print(f"  Total Years: {total_years}")
        print(f"  Completeness: {criteria.get('completeness', 'N/A')}")
        print(f"  Skills: {criteria.get('skills', 'N/A')}")
        print(f"  Professionalism: {criteria.get('professionalism', 'N/A')}")
        
        return {
            'overall_score': overall_score,
            'experience_score': experience_score,
            'total_years': total_years
        }
    else:
        print(f"❌ Failed to get analysis: {response.status_code}")
        return None


def main():
    """Main test flow"""
    print("=" * 60)
    print("🧪 EXPERIENCE SCORING BUG TEST")
    print("=" * 60)
    
    # Step 1: Login
    if not login():
        print("\n❌ Cannot proceed without authentication")
        return
    
    # Step 2: Upload CV with 21+ years experience
    print("\n" + "=" * 60)
    print("TEST 1: CV with 21+ years experience")
    print("=" * 60)
    
    cv_id_21 = upload_cv(CV_21_YEARS)
    if not cv_id_21:
        print("❌ Failed to upload first CV")
        return
    
    if wait_for_analysis(cv_id_21):
        results_21 = get_analysis_results(cv_id_21)
    else:
        print("❌ Analysis did not complete for first CV")
        results_21 = None
    
    # Step 3: Upload CV with 3 years experience
    print("\n" + "=" * 60)
    print("TEST 2: CV with 3 years experience")
    print("=" * 60)
    
    cv_id_3 = upload_cv(CV_3_YEARS)
    if not cv_id_3:
        print("❌ Failed to upload second CV")
        return
    
    if wait_for_analysis(cv_id_3):
        results_3 = get_analysis_results(cv_id_3)
    else:
        print("❌ Analysis did not complete for second CV")
        results_3 = None
    
    # Step 4: Compare results
    print("\n" + "=" * 60)
    print("📊 COMPARISON RESULTS")
    print("=" * 60)
    
    if results_21 and results_3:
        print(f"\nCV with 21+ years:")
        print(f"  Experience Score: {results_21['experience_score']}")
        print(f"  Total Years: {results_21['total_years']}")
        
        print(f"\nCV with 3 years:")
        print(f"  Experience Score: {results_3['experience_score']}")
        print(f"  Total Years: {results_3['total_years']}")
        
        # Check for bug
        if results_21['experience_score'] == results_3['experience_score']:
            print("\n🚨 BUG CONFIRMED: Both CVs have the same experience score!")
            print(f"   21 years = {results_21['experience_score']}")
            print(f"   3 years = {results_3['experience_score']}")
        else:
            print("\n✅ Experience scores are different (as expected)")
    else:
        print("\n❌ Could not compare results (missing data)")
    
    print("\n" + "=" * 60)
    print("🔍 Check backend logs for detailed debug information")
    print("=" * 60)


if __name__ == "__main__":
    main()
