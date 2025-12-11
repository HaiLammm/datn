#!/usr/bin/env python3
"""
Simple test script to verify CV upload functionality
"""
import asyncio
import aiofiles
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

async def test_cv_upload():
    """Test CV upload functionality"""
    print("Testing CV upload functionality...")

    # Create test client
    client = TestClient(app)

    # Read the CV file
    cv_file_path = Path("../cv/cv2.pdf")
    if not cv_file_path.exists():
        print(f"❌ CV file not found: {cv_file_path}")
        return

    print(f"✅ Found CV file: {cv_file_path}")

    # Read file content
    async with aiofiles.open(cv_file_path, 'rb') as f:
        file_content = await f.read()

    print(f"✅ Read {len(file_content)} bytes from CV file")

    # Prepare multipart form data
    files = {
        "file": ("cv2.pdf", file_content, "application/pdf")
    }

    print("📤 Attempting to upload CV...")

    # Note: This will fail without authentication, but let's see what happens
    response = client.post("/api/v1/cvs/", files=files)

    print(f"📊 Response status: {response.status_code}")
    print(f"📊 Response: {response.json()}")

    if response.status_code == 401:
        print("✅ Authentication required (expected)")
    elif response.status_code == 201:
        print("✅ CV uploaded successfully!")
    else:
        print(f"❌ Unexpected response: {response.status_code}")

if __name__ == "__main__":
    asyncio.run(test_cv_upload())