#!/usr/bin/env python3
"""
Debug script to investigate the candidates endpoint issue.
"""

import asyncio
import os
import sys
from uuid import UUID

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "."))

from sqlalchemy.ext.asyncio import create_async_session
from app.core.database import get_db_engine
from app.modules.jobs.service import JobService
from app.modules.jobs.candidate_ranker import CandidateRanker
from app.modules.cv.models import CV, CVAnalysisStatus
from app.modules.jobs.models import JobDescription, JDParseStatus
from sqlalchemy import select, func

async def check_jd_and_candidates(jd_id_str: str):
    """Check the status of a specific JD and available candidates."""
    
    print(f"🔍 Investigating JD: {jd_id_str}")
    print("=" * 60)
    
    try:
        jd_id = UUID(jd_id_str)
    except ValueError:
        print("❌ Invalid UUID format")
        return
    
    # Create async session
    engine = get_db_engine()
    async with engine.begin() as conn:
        from sqlalchemy.ext.asyncio import AsyncSession
        session = AsyncSession(conn)
        
        # 1. Check if JD exists
        print("\n1️⃣  Checking if JD exists...")
        jd_result = await session.execute(
            select(JobDescription).where(JobDescription.id == jd_id)
        )
        jd = jd_result.scalars().first()
        
        if not jd:
            print("❌ JD not found in database")
            return
            
        print(f"✅ JD found: {jd.title}")
        print(f"   - Parse status: {jd.parse_status}")
        print(f"   - Created by user: {jd.user_id}")
        print(f"   - Created at: {jd.created_at}")
        
        # 2. Check parsing status
        print("\n2️⃣  Checking JD parsing status...")
        if jd.parse_status != JDParseStatus.COMPLETED.value:
            print(f"⚠️  JD parsing not complete: {jd.parse_status}")
            print("   This would cause a 409 Conflict error")
            return
        else:
            print("✅ JD parsing completed")
            
        # 3. Check parsed requirements
        print("\n3️⃣  Checking parsed requirements...")
        if not jd.parsed_requirements:
            print("❌ No parsed requirements found")
            print("   This would cause a ValueError")
            return
        else:
            print("✅ Parsed requirements exist")
            # Show first 100 chars
            requirements_str = str(jd.parsed_requirements)[:100]
            print(f"   Preview: {requirements_str}...")
            
        # 4. Check available CVs
        print("\n4️⃣  Checking available CVs...")
        cv_count_result = await session.execute(
            select(func.count(CV.id))
            .where(CV.analysis_status == CVAnalysisStatus.COMPLETED.value)
        )
        cv_count = cv_count_result.scalar()
        print(f"📊 Total completed CV analyses: {cv_count}")
        
        if cv_count == 0:
            print("⚠️  No completed CV analyses found")
            print("   This would result in an empty candidate list")
            return
            
        # 5. Try the candidate ranker
        print("\n5️⃣  Testing candidate ranker...")
        try:
            ranker = CandidateRanker()
            candidates, total = await ranker.rank_candidates(
                db=session,
                jd_id=jd_id,
                limit=5,
                offset=0,
                min_score=0,
            )
            print(f"✅ Candidate ranking successful")
            print(f"   - Total candidates found: {total}")
            print(f"   - Candidates returned: {len(candidates)}")
            
            if candidates:
                print(f"\n📋 Top candidate scores:")
                for i, candidate in enumerate(candidates[:3], 1):
                    print(f"   {i}. CV {candidate.cv_id}: {candidate.match_score:.1f}%")
            
        except Exception as e:
            print(f"❌ Candidate ranker error: {e}")
            print(f"   Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            
        # 6. Test job service
        print("\n6️⃣  Testing job service...")
        try:
            job_service = JobService()
            jd_result = await job_service.get_job_description(session, jd_id, jd.user_id)
            if jd_result:
                print("✅ Job service can retrieve JD")
            else:
                print("❌ Job service cannot retrieve JD")
        except Exception as e:
            print(f"❌ Job service error: {e}")

    print("\n" + "=" * 60)
    print("🏁 Investigation complete!")

async def main():
    """Main function."""
    if len(sys.argv) != 2:
        print("Usage: python debug_candidates_issue.py <jd_id>")
        print("Example: python debug_candidates_issue.py 68dacfcc-0c9c-4e8d-a7ad-93404182ffaa")
        sys.exit(1)
        
    jd_id = sys.argv[1]
    await check_jd_and_candidates(jd_id)

if __name__ == "__main__":
    asyncio.run(main())