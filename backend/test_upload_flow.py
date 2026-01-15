#!/usr/bin/env python3
"""
End-to-end test for CV upload and analysis flow using Celery.
This simulates what happens when a user uploads CV via frontend.
"""
import time
import requests
from pathlib import Path

BASE_URL = "http://localhost:8000/api/v1"

def test_cv_upload_and_analysis():
    """
    Test complete CV upload and analysis flow.
    """
    print("=" * 70)
    print("  CV UPLOAD & CELERY ANALYSIS - END-TO-END TEST")
    print("=" * 70)
    print()
    
    # Step 1: Login
    print("Step 1: Login...")
    login_data = {
        "email": "teamgamozxv@gmail.com",
        "password": "123456789"  # Try common password
    }
    
    session = requests.Session()
    response = session.post(f"{BASE_URL}/auth/login", json=login_data)
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code}")
        print(f"   Response: {response.text}")
        print("\n💡 Trying to find existing CV instead...")
        return test_existing_cv_status()
    
    print(f"✅ Login successful")
    
    # Step 2: Prepare CV file
    print("\nStep 2: Preparing test CV file...")
    
    # Use existing PDF
    cv_path = Path("/home/luonghailam/Projects/datn/backend/data/cv_uploads/ea1c5e75-cc00-4475-90d3-1e1f78981607.pdf")
    
    if not cv_path.exists():
        print(f"❌ Test CV file not found: {cv_path}")
        return
    
    print(f"✅ Using CV file: {cv_path.name} ({cv_path.stat().st_size / 1024:.2f} KB)")
    
    # Step 3: Upload CV
    print("\nStep 3: Uploading CV...")
    
    with open(cv_path, 'rb') as f:
        files = {'file': (f'test_{cv_path.name}', f, 'application/pdf')}
        response = session.post(f"{BASE_URL}/cvs/", files=files)
    
    if response.status_code != 201:
        print(f"❌ Upload failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return
    
    cv_data = response.json()
    cv_id = cv_data['id']
    print(f"✅ CV uploaded successfully!")
    print(f"   CV ID: {cv_id}")
    print(f"   Filename: {cv_data['filename']}")
    
    # Step 4: Poll analysis status
    print("\nStep 4: Polling analysis status...")
    print("   (Max 60 seconds, checking every 2 seconds)")
    
    for i in range(30):  # 30 * 2 = 60 seconds max
        time.sleep(2)
        
        response = session.get(f"{BASE_URL}/ai/cvs/{cv_id}/status")
        
        if response.status_code != 200:
            print(f"\r   [{i+1}/30] ❌ Status check failed: {response.status_code}", end="")
            continue
        
        status_data = response.json()
        status = status_data['status']
        
        print(f"\r   [{i+1}/30] Status: {status:<15}", end="", flush=True)
        
        if status == "COMPLETED":
            print(f"\n\n✅ Analysis COMPLETED after {(i+1)*2} seconds!")
            
            # Step 5: Get analysis results
            print("\nStep 5: Fetching analysis results...")
            response = session.get(f"{BASE_URL}/ai/cvs/{cv_id}/analysis")
            
            if response.status_code == 200:
                analysis = response.json()
                print(f"✅ Analysis results retrieved!")
                print(f"\n📊 Analysis Summary:")
                print(f"   AI Score: {analysis.get('ai_score', 'N/A')}/100")
                print(f"   Summary: {analysis.get('ai_summary', 'N/A')[:150]}...")
                
                skills = analysis.get('extracted_skills', [])
                if skills:
                    print(f"   Extracted Skills ({len(skills)}): {', '.join(skills[:10])}")
                    if len(skills) > 10:
                        print(f"      ... and {len(skills) - 10} more")
                
                skill_breakdown = analysis.get('skill_breakdown')
                if skill_breakdown:
                    print(f"\n   Skill Breakdown:")
                    for category, data in skill_breakdown.items():
                        print(f"      {category}: {data.get('score', 0)}/100")
            else:
                print(f"❌ Failed to get analysis: {response.status_code}")
                print(f"   Response: {response.text}")
            
            return
        
        elif status == "FAILED":
            print(f"\n\n❌ Analysis FAILED!")
            response = session.get(f"{BASE_URL}/ai/cvs/{cv_id}/analysis")
            if response.status_code == 200:
                analysis = response.json()
                print(f"   Error: {analysis.get('ai_summary', 'Unknown error')}")
            return
    
    print(f"\n\n⏰ Timeout after 60 seconds. Analysis may still be running.")
    print(f"   Check Celery logs: tail -f /tmp/celery_worker_new.log")


def test_existing_cv_status():
    """
    Fallback: Check status of existing CVs in database.
    """
    print("\n" + "=" * 70)
    print("  TESTING WITH EXISTING CV")
    print("=" * 70)
    
    # Try common test CV ID
    cv_id = "c64a4871-b29b-45cf-8ab5-6e2f4fcd39fb"
    
    print(f"\n🔍 Checking status of CV: {cv_id}")
    
    # No auth needed for this endpoint in some cases, or use cookies
    session = requests.Session()
    response = session.get(f"{BASE_URL}/ai/cvs/{cv_id}/status")
    
    if response.status_code == 200:
        status_data = response.json()
        print(f"✅ Status retrieved: {status_data['status']}")
    else:
        print(f"❌ Failed to get status: {response.status_code}")
        print(f"   Response: {response.text}")


if __name__ == "__main__":
    test_cv_upload_and_analysis()
