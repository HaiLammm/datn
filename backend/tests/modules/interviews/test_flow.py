import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.modules.users.models import User as DBUser
from app.modules.interviews.schemas import InterviewCreateResponse
from app.modules.auth.dependencies import get_current_user, require_job_seeker
from app.main import app

# Fixture for candidate user
@pytest.fixture
def candidate_user() -> DBUser:
    return DBUser(
        id=2,
        email="candidate@test.com",
        hashed_password="pw",
        role="job_seeker",
        is_active=True,
    )

@pytest.mark.asyncio
async def test_create_interview_flow(async_client, candidate_user, mock_db_session):
    # Override auth to be candidate
    app.dependency_overrides[get_current_user] = lambda: candidate_user
    app.dependency_overrides[require_job_seeker] = lambda: candidate_user 

    # Mock the EXISTING agent instance on the global interview_service
    from app.modules.interviews.router import interview_service
    
    # Create a mock for the generate_questions method
    mock_generate = MagicMock(return_value={
        "status": "success",
        "questions": [
            {
                "question_id": "Q1",
                "category": "technical",
                "difficulty": "middle",
                "question_text": "What is React?",
                "key_points": ["Library", "Components"],
                "ideal_answer_outline": "React is...",
                "evaluation_criteria": ["Mention components"],
            }
        ],
        "metadata": {
            "total_questions": 1,
            "distribution": {"technical": 1}
        }
    })
    
    # Store original method to restore after test (optional but good practice)
    original_method = interview_service.question_service.agent.generate_questions
    interview_service.question_service.agent.generate_questions = mock_generate

    try:
        # Mock DB behavior
        # session.add, session.commit, session.refresh
        async def mock_refresh(obj):
            if not hasattr(obj, 'id') or obj.id is None:
                import uuid
                obj.id = uuid.uuid4()
            return None
            
        def mock_add(obj):
            if not hasattr(obj, 'id') or obj.id is None:
                import uuid
                obj.id = uuid.uuid4()
            
            # Simulate timestamps
            from datetime import datetime
            now = datetime.utcnow()
            if hasattr(obj, 'created_at') and getattr(obj, 'created_at', None) is None:
                obj.created_at = now
            if hasattr(obj, 'updated_at') and getattr(obj, 'updated_at', None) is None:
                obj.updated_at = now
        
        mock_db_session.refresh.side_effect = mock_refresh
        mock_db_session.add.side_effect = mock_add

        payload = {
            "job_description": "We need a React developer with Node.js skills.",
            "cv_content": "I am a Full Stack Developer with React experience.",
            "position_level": "middle",
            "num_questions": 5,
            "focus_areas": ["React", "System Design"]
        }

        response = await async_client.post("/api/v1/interviews", json=payload)

        if response.status_code != 201:
            print(f"\nAPI Error: {response.text}\n")
        assert response.status_code == 201
        data = response.json()
        assert "session" in data
        assert "questions" in data
        assert len(data["questions"]) == 1
        assert data["questions"][0]["question_text"] == "What is React?"
        
        # Verify agent was called
        mock_generate.assert_called_once()
        
    finally:
        # Restore
        interview_service.question_service.agent.generate_questions = original_method
    
    app.dependency_overrides.clear()
