import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import asyncio
from app.core.database import AsyncSessionLocal
from app.modules.interviews.models import InterviewSession
from sqlalchemy import select, update
from datetime import datetime, timezone

async def fix_stuck():
    async with AsyncSessionLocal() as session:
        # Update stuck "generating" sessions
        result = await session.execute(
            update(InterviewSession)
            .where(InterviewSession.status == 'generating')
            .values(
                status='error',
                error_message='Worker was restarted during generation',
                updated_at=datetime.now(timezone.utc)
            )
        )
        await session.commit()
        print(f"✅ Fixed {result.rowcount} stuck 'generating' sessions")
        
        # Check result
        result = await session.execute(
            select(InterviewSession).where(InterviewSession.status == 'error')
        )
        error_sessions = result.scalars().all()
        for s in error_sessions:
            print(f"   - {s.id}: {s.error_message}")

asyncio.run(fix_stuck())
