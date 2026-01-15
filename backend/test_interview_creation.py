import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import async_session_maker
from app.modules.interviews.models import InterviewSession
from app.modules.cv.models import CV
from app.modules.jobs.models import JobDescription
from sqlalchemy import select
import uuid

async def test_interview_creation():
    """Test creating an interview session via task"""
    
    async with async_session_maker() as db_session:
        # 1. Find an analyzed CV
        result = await db_session.execute(
            select(CV).where(CV.is_active == True).limit(1)
        )
        cv = result.scalar_one_or_none()
        
        if not cv:
            print("❌ No CV found in database")
            return
        
        print(f"✅ Found CV: {cv.id} (user_id: {cv.user_id})")
        
        # 2. Find a job description
        result = await db_session.execute(
            select(JobDescription).where(JobDescription.is_active == True).limit(1)
        )
        jd = result.scalar_one_or_none()
        
        if not jd:
            print("❌ No Job Description found")
            return
            
        print(f"✅ Found Job: {jd.id} - {jd.title}")
        
        # 3. Create interview session
        from app.modules.interviews.tasks import generate_questions_task
        
        session_id = uuid.uuid4()
        print(f"\n📝 Creating interview session: {session_id}")
        
        # Trigger async task
        task = generate_questions_task.delay(
            session_id=str(session_id),
            cv_id=str(cv.id),
            job_id=str(jd.id),
            user_id=cv.user_id,
            num_questions=5
        )
        
        print(f"✅ Task submitted: {task.id}")
        print(f"⏳ Task state: {task.state}")
        
        # 4. Monitor task progress
        print("\n⏳ Waiting for task to complete (max 3 minutes)...")
        for i in range(36):  # 36 * 5 = 180 seconds
            await asyncio.sleep(5)
            task_state = task.state
            print(f"   [{i*5}s] Task state: {task_state}")
            
            if task_state in ['SUCCESS', 'FAILURE']:
                break
        
        # 5. Check final result
        if task.state == 'SUCCESS':
            print(f"\n✅ Task completed successfully!")
            result = task.result
            print(f"   Result: {result}")
            
            # Check database
            result = await db_session.execute(
                select(InterviewSession).where(InterviewSession.id == session_id)
            )
            interview = result.scalar_one_or_none()
            
            if interview:
                print(f"\n✅ Interview session created:")
                print(f"   - ID: {interview.id}")
                print(f"   - Status: {interview.status}")
                print(f"   - Questions count: {len(interview.questions) if interview.questions else 0}")
                
                if interview.questions:
                    print(f"\n📋 Generated Questions:")
                    for idx, q in enumerate(interview.questions[:3], 1):
                        print(f"   {idx}. [{q.category}] {q.question_text[:80]}...")
            else:
                print(f"⚠️ Interview session not found in database")
                
        elif task.state == 'FAILURE':
            print(f"\n❌ Task failed!")
            print(f"   Error: {task.info}")
        else:
            print(f"\n⚠️ Task timed out (state: {task.state})")

if __name__ == "__main__":
    asyncio.run(test_interview_creation())
