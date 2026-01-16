"""Test the generate-next-question endpoint directly."""
import asyncio
import sys
from uuid import UUID

# Import all models first to avoid SQLAlchemy issues
from app.modules.users.models import User
from app.modules.cv.models import CV
from app.modules.ai.models import CVAnalysis
from app.modules.interviews.models import InterviewSession

from app.core.database import AsyncSessionLocal
from app.modules.interviews.router import generate_next_question
from app.modules.auth.dependencies import get_current_user

class MockUser:
    def __init__(self, user_id):
        self.id = user_id
        self.role = "job_seeker"

async def test_generate_question(session_id: str, user_id: int):
    """Test generating a question."""
    async with AsyncSessionLocal() as db:
        try:
            print(f"Testing generate_next_question for session {session_id}, user {user_id}")
            
            # Create mock user
            mock_user = MockUser(user_id)
            
            # Call the endpoint function directly
            result = await generate_next_question(
                session_id=UUID(session_id),
                current_user=mock_user,
                db=db
            )
            
            print(f"✅ Success!")
            print(f"  Question: {result.question.question_text[:100]}...")
            print(f"  Category: {result.question.category}")
            print(f"  Question {result.question_number}/{result.total_questions}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python test_endpoint.py <session_id> <user_id>")
        print("Example: python test_endpoint.py 68a6bdfd-fcef-4f02-83b5-92f27301908b 14")
        sys.exit(1)
    
    session_id = sys.argv[1]
    user_id = int(sys.argv[2])
    
    asyncio.run(test_generate_question(session_id, user_id))
