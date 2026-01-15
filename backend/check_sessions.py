import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import asyncio
from app.core.database import AsyncSessionLocal
from app.modules.interviews.models import InterviewSession, InterviewQuestion
from sqlalchemy import select, desc, func

async def check_sessions():
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(InterviewSession)
            .order_by(desc(InterviewSession.created_at))
            .limit(5)
        )
        sessions = result.scalars().all()
        
        if not sessions:
            print("❌ No interview sessions found")
            return
            
        print(f"📊 Recent Interview Sessions:\n")
        for s in sessions:
            # Count questions separately to avoid lazy loading
            q_result = await session.execute(
                select(func.count()).select_from(InterviewQuestion).where(
                    InterviewQuestion.interview_session_id == s.id
                )
            )
            q_count = q_result.scalar()
            
            print(f"ID: {s.id}")
            print(f"   Status: {s.status}")
            print(f"   Created: {s.created_at}")
            print(f"   Questions: {q_count}")
            print(f"   Error: {s.error_message if s.error_message else 'None'}")
            print()

asyncio.run(check_sessions())
