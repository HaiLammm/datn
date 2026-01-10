"""
Pytest configuration and shared fixtures for all tests
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


# Sample test data fixtures
@pytest.fixture
def sample_job_description():
    """Sample job description for testing"""
    return """
    Tuyển dụng Backend Developer
    
    Yêu cầu:
    - 2+ năm kinh nghiệm Python/FastAPI
    - Thành thạo SQL, PostgreSQL
    - Kinh nghiệm với Docker, CI/CD
    - Hiểu biết về RESTful API design
    - Am hiểu về authentication, authorization
    
    Ưu tiên:
    - Có kinh nghiệm với Microservices
    - Biết Redis, Celery
    """


@pytest.fixture
def sample_cv():
    """Sample CV for testing"""
    return """
    Nguyễn Văn A
    Backend Developer
    
    Kinh nghiệm:
    - 3 năm làm việc với Python, Django, FastAPI
    - Phát triển RESTful APIs cho ứng dụng e-commerce
    - Thiết kế database schema với PostgreSQL
    - Triển khai CI/CD với GitLab CI
    - Sử dụng Docker cho containerization
    
    Kỹ năng:
    - Python, FastAPI, Django
    - PostgreSQL, MySQL
    - Docker, Kubernetes cơ bản
    - Git, GitLab CI/CD
    - Redis, Celery
    """


@pytest.fixture
def sample_question():
    """Sample interview question for testing"""
    return {
        "question_id": "Q1",
        "category": "technical",
        "difficulty": "middle",
        "question_text": "Bạn có thể giải thích cách FastAPI xử lý async/await khác với Django như thế nào?",
        "key_points": [
            "ASGI vs WSGI",
            "Async/await trong Python",
            "Use cases cho async"
        ],
        "ideal_answer_outline": "Ứng viên nên giải thích FastAPI chạy trên ASGI...",
        "evaluation_criteria": [
            "Hiểu rõ khái niệm async/await",
            "So sánh chính xác FastAPI vs Django"
        ]
    }


@pytest.fixture
def sample_candidate_answer():
    """Sample candidate answer for testing"""
    return """
    FastAPI chạy trên ASGI nên có thể xử lý async tốt hơn Django. 
    Em đã dùng async cho external API calls trong dự án, 
    giúp server không bị block khi đợi response.
    """


@pytest.fixture
def sample_conversation_history():
    """Sample conversation history for testing"""
    return [
        {
            "turn_id": 0,
            "question": "Giới thiệu về bản thân?",
            "answer": "Em là Nguyễn Văn A, 3 năm kinh nghiệm backend...",
            "score": 8.0
        }
    ]


@pytest.fixture
def sample_interview_transcript():
    """Sample full interview transcript for testing"""
    return [
        {
            "turn_id": 0,
            "ai_message": "Xin chào! Em có thể giới thiệu về kinh nghiệm với Python không?",
            "candidate_message": "Xin chào anh! Em có 3 năm kinh nghiệm với Python..."
        },
        {
            "turn_id": 1,
            "ai_message": "Bạn có thể giải thích cách FastAPI xử lý async/await không?",
            "candidate_message": "FastAPI chạy trên ASGI nên có thể xử lý async tốt hơn..."
        }
    ]


@pytest.fixture
def sample_turn_evaluations():
    """Sample per-turn evaluations for testing"""
    return [
        {
            "turn_id": 1,
            "answer_quality": {
                "technical_accuracy": 8.0,
                "communication_clarity": 8.5,
                "depth_of_knowledge": 7.5,
                "overall_score": 8.0
            },
            "key_observations": ["Hiểu ASGI", "Có kinh nghiệm thực tế"]
        }
    ]


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test requiring Ollama"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as performance test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to handle markers"""
    if not config.getoption("--run-integration"):
        skip_integration = pytest.mark.skip(reason="need --run-integration option to run")
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip_integration)
