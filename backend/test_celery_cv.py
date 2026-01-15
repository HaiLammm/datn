#!/usr/bin/env python3
"""
Test script to trigger Celery CV analysis task manually.
This simulates what happens when a CV is uploaded via the API.
"""
import asyncio
import sys
import uuid
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

# Import all models in dependency order to ensure relationships are resolved
from app.modules.users.models import User
from app.modules.jobs.models import JobDescription, Application
from app.modules.cv.models import CV
from app.modules.ai.models import CVAnalysis, AnalysisStatus
from app.core.database import AsyncSessionLocal
from app.modules.ai.tasks import analyze_cv_task


async def create_test_cv_analysis(cv_file_path: str):
    """
    Create a test CV record and trigger Celery analysis.
    
    Args:
        cv_file_path: Path to an existing CV file to analyze
    """
    file_path = Path(cv_file_path)
    
    if not file_path.exists():
        print(f"❌ File not found: {cv_file_path}")
        return
    
    print(f"📄 Testing with CV file: {file_path.name}")
    print(f"   File size: {file_path.stat().st_size / 1024:.2f} KB")
    
    async with AsyncSessionLocal() as db:
        # Create test CV record
        test_cv = CV(
            user_id=1,  # Assuming user ID 1 exists (teamgamozxv@gmail.com)
            filename=f"TEST_{file_path.name}",
            file_path=str(file_path),
            is_active=True
        )
        db.add(test_cv)
        await db.commit()
        await db.refresh(test_cv)
        
        cv_id = test_cv.id
        print(f"✅ Created test CV record: {cv_id}")
        
        # Create CVAnalysis record
        analysis = CVAnalysis(
            cv_id=cv_id,
            status=AnalysisStatus.PENDING
        )
        db.add(analysis)
        await db.commit()
        
        print(f"✅ Created CVAnalysis record with status: PENDING")
        
        # Trigger Celery task
        print(f"\n🚀 Dispatching Celery task...")
        task = analyze_cv_task.delay(str(cv_id), str(file_path))
        
        print(f"✅ Celery task dispatched!")
        print(f"   Task ID: {task.id}")
        print(f"   CV ID: {cv_id}")
        print(f"   File: {file_path}")
        print(f"\n📊 Monitor task status:")
        print(f"   - Watch Celery logs: tail -f /tmp/celery_worker.log")
        print(f"   - Check task state: task.state = {task.state}")
        print(f"\n🔍 Check analysis status in DB:")
        print(f"   SELECT status FROM cv_analyses WHERE cv_id = '{cv_id}';")
        
        # Poll task status for 30 seconds
        print(f"\n⏳ Polling task status (30 seconds)...")
        for i in range(30):
            await asyncio.sleep(1)
            
            # Refresh analysis from DB
            await db.refresh(analysis)
            status = analysis.status.value if hasattr(analysis.status, 'value') else str(analysis.status)
            
            print(f"   [{i+1}/30] Status: {status}", end="\r")
            
            if status in ["COMPLETED", "FAILED"]:
                print(f"\n\n✅ Analysis finished with status: {status}")
                
                if status == "COMPLETED":
                    print(f"   AI Score: {analysis.ai_score}")
                    print(f"   Summary: {analysis.ai_summary[:100] if analysis.ai_summary else 'N/A'}...")
                    if analysis.extracted_skills:
                        print(f"   Extracted Skills: {len(analysis.extracted_skills)} skills")
                else:
                    print(f"   Summary: {analysis.ai_summary}")
                
                break
        else:
            print(f"\n\n⏰ Timeout after 30 seconds. Task may still be running.")
            print(f"   Current status: {status}")
            print(f"   Check Celery logs for details.")


if __name__ == "__main__":
    # Use an existing CV file
    cv_path = "/home/luonghailam/Projects/datn/backend/data/cv_uploads/c64a4871-b29b-45cf-8ab5-6e2f4fcd39fb.pdf"
    
    print("=" * 70)
    print("  CELERY CV ANALYSIS TEST")
    print("=" * 70)
    print()
    
    asyncio.run(create_test_cv_analysis(cv_path))
