#!/usr/bin/env python3
"""
Test script to verify CV upload functionality with authentication
"""
import asyncio
import aiofiles
from pathlib import Path
import requests

async def test_authenticated_cv_upload():
    """Test CV upload with proper authentication"""
    print("🧪 Testing authenticated CV upload functionality...")

    # Backend URLs
    base_url = "http://localhost:8000"
    login_url = f"{base_url}/api/v1/auth/login"
    upload_url = f"{base_url}/api/v1/cvs"

    # Test credentials
    test_email = "test@example.com"
    test_password = "password123"

    session = requests.Session()

    try:
        print(f"👤 Attempting to register test user {test_email}...")

        # First, try to register a test user
        register_data = {
            "email": test_email,
            "password": test_password,
            "full_name": "Test User",
            "birthday": "1990-01-01"
        }

        register_response = session.post(f"{base_url}/api/v1/auth/register", json=register_data)

        if register_response.status_code == 201:
            print("✅ Test user registered successfully!")
        elif register_response.status_code == 400:
            print("ℹ️  Test user may already exist, proceeding with login...")
        else:
            print(f"❌ Registration failed: {register_response.status_code} - {register_response.text}")
            return

        print(f"🔐 Attempting login with {test_email}...")

        # Now try to login
        login_data = {
            "email": test_email,
            "password": test_password
        }

        login_response = session.post(login_url, json=login_data)

        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code} - {login_response.text}")
            print("💡 You may need to create a test user first or adjust credentials")
            return

        print("✅ Login successful!")

        # Read the CV file
        cv_file_path = Path("../cv/Lam-Luong-Hai-TopCV.vn-101125.84317.pdf")
        if not cv_file_path.exists():
            print(f"❌ CV file not found: {cv_file_path}")
            return

        print(f"📄 Found CV file: {cv_file_path} ({cv_file_path.stat().st_size} bytes)")

        # Read file content
        async with aiofiles.open(cv_file_path, 'rb') as f:
            file_content = await f.read()

        print(f"📤 Attempting to upload CV...")

        # Prepare multipart form data
        files = {
            "file": ("Lam-Luong-Hai-TopCV.vn-101125.84317.pdf", file_content, "application/pdf")
        }

        # Upload with the authenticated session
        upload_response = session.post(upload_url, files=files)

        print(f"📊 Upload response status: {upload_response.status_code}")

        if upload_response.status_code == 201:
            print("✅ CV uploaded successfully!")
            print(f"📋 Response: {upload_response.json()}")

            # Check if file was saved
            cv_data = upload_response.json()
            file_path = cv_data.get('file_path')
            if file_path and Path(file_path).exists():
                print(f"💾 File saved successfully at: {file_path}")
            else:
                print(f"⚠️  File path not found or doesn't exist: {file_path}")

        elif upload_response.status_code == 429:
            print("⚠️  Rate limit exceeded (expected with multiple tests)")
        else:
            print(f"❌ Upload failed: {upload_response.text}")

    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Is it running on http://localhost:8000?")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_authenticated_cv_upload())