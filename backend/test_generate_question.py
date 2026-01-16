"""Test script to generate a single question and debug any errors."""
import asyncio
import sys
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

# Import all models to ensure SQLAlchemy mappers are initialized
from app.modules.users.models import User
from app.modules.cv.models import CV
from app.modules.ai.models import CVAnalysis

from app.core.database import AsyncSessionLocal
from app.modules.interviews.service import InterviewService

interview_service = InterviewService()

async def test_generate_question(session_id: str, user_id: int):
    """Test generating a single question."""
    async with AsyncSessionLocal() as db:
        try:
            print(f"Attempting to generate question for session {session_id}, user {user_id}")
            question = await interview_service.question_service.generate_single_question(
                db=db,
                session_id=UUID(session_id),
                user_id=user_id
            )
            print(f"✅ Success! Generated question:")
            print(f"  ID: {question.id}")
            print(f"  Text: {question.question_text}")
            print(f"  Category: {question.category}")
            print(f"  Difficulty: {question.difficulty}")
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python test_generate_question.py <session_id> <user_id>")
        print("Example: python test_generate_question.py e94b99ad-3c9b-4510-b573-74c43b69d859 14")
        sys.exit(1)
    
    session_id = sys.argv[1]
    user_id = int(sys.argv[2])
    
    asyncio.run(test_generate_question(session_id, user_id))
