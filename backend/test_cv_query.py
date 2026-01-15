#!/usr/bin/env python3
"""
Script to test CV query and diagnose the 500 error
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

# Import all models FIRST to register relationships
from app.modules.users.models import User
from app.modules.jobs.models import JobDescription, Application
from app.modules.cv.models import CV
from app.modules.ai.models import CVAnalysis

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.core.database import AsyncSessionLocal


async def test_cv_query():
    """Test the exact query that's failing in the router"""
    print("🔍 Testing CV Query...")
    print("=" * 60)
    
    async with AsyncSessionLocal() as db:
        try:
            # Test 1: Check if user exists
            print("\n1️⃣ Checking users table...")
            user_result = await db.execute(select(User))
            users = user_result.scalars().all()
            print(f"   ✅ Found {len(users)} users")
            if users:
                test_user = users[0]
                print(f"   📧 Test user: {test_user.email} (ID: {test_user.id})")
            else:
                print("   ⚠️  No users found in database")
                return
            
            # Test 2: Check CVs table
            print("\n2️⃣ Checking CVs table...")
            cv_result = await db.execute(select(CV))
            cvs = cv_result.scalars().all()
            print(f"   ✅ Found {len(cvs)} CVs")
            
            # Test 3: Check CVAnalysis table
            print("\n3️⃣ Checking cv_analyses table...")
            analysis_result = await db.execute(select(CVAnalysis))
            analyses = analysis_result.scalars().all()
            print(f"   ✅ Found {len(analyses)} analyses")
            
            # Test 4: Try the exact query from the router
            print("\n4️⃣ Testing exact router query with selectinload...")
            try:
                result = await db.execute(
                    select(CV)
                    .options(selectinload(CV.analyses))
                    .where(CV.user_id == test_user.id)
                    .order_by(CV.uploaded_at.desc())
                )
                cvs_with_analyses = result.scalars().all()
                print(f"   ✅ Query successful! Found {len(cvs_with_analyses)} CVs for user")
                
                # Test 5: Process like the router does
                print("\n5️⃣ Testing response building...")
                for cv in cvs_with_analyses:
                    analysis = cv.analyses[0] if cv.analyses else None
                    if analysis:
                        status_str = analysis.status.value if hasattr(analysis.status, "value") else str(analysis.status)
                        quality_score = analysis.ai_score
                        print(f"   📄 CV: {cv.filename}")
                        print(f"      Status: {status_str}")
                        print(f"      Score: {quality_score}")
                    else:
                        print(f"   📄 CV: {cv.filename}")
                        print(f"      Status: PENDING (no analysis)")
                
                print("\n✅ All tests passed! Query works fine.")
                
            except Exception as e:
                print(f"   ❌ Query failed!")
                print(f"   Error type: {type(e).__name__}")
                print(f"   Error message: {str(e)}")
                import traceback
                print("\n   Full traceback:")
                traceback.print_exc()
                
        except Exception as e:
            print(f"\n❌ Database connection or query failed!")
            print(f"Error type: {type(e).__name__}")
            print(f"Error message: {str(e)}")
            import traceback
            traceback.print_exc()


async def test_db_connection():
    """Test basic database connection"""
    print("🔌 Testing database connection...")
    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(1))
            print("✅ Database connection successful!")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


async def main():
    print("🚀 CV Query Diagnostic Tool")
    print("=" * 60)
    
    # Test connection first
    if not await test_db_connection():
        print("\n⚠️  Fix database connection first!")
        return
    
    # Run the query test
    await test_cv_query()
    
    print("\n" + "=" * 60)
    print("✅ Diagnostic complete!")


if __name__ == "__main__":
    asyncio.run(main())
