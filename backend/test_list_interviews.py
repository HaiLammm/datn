import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import asyncio
from app.core.database import AsyncSessionLocal
from app.modules.interviews.models import InterviewSession
from sqlalchemy import select, func

async def test_list():
    async with AsyncSessionLocal() as session:
        # Count total interviews
        result = await session.execute(
            select(func.count()).select_from(InterviewSession)
        )
        total = result.scalar()
        print(f"📊 Total interviews in database: {total}")
        
        # Get first 5
        result = await session.execute(
            select(InterviewSession).limit(5)
        )
        interviews = result.scalars().all()
        
        print(f"\n📋 First 5 interviews:")
        for i in interviews:
            print(f"  - {i.id}: status={i.status}, created={i.created_at}")

asyncio.run(test_list())
