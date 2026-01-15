"""
Celery application instance for async task processing.

This module configures Celery to work with Redis as message broker
and result backend for Epic 8: AI Interview Room background tasks.
"""
from celery import Celery
from app.core.config import settings

# CRITICAL: Import all models BEFORE Celery app initialization
# This ensures SQLAlchemy relationships are properly resolved
from app.modules.users.models import User
from app.modules.jobs.models import JobDescription, Application
from app.modules.cv.models import CV
from app.modules.ai.models import CVAnalysis, AnalysisStatus
from app.modules.interviews.models import (
    InterviewSession,
    InterviewQuestion,
    InterviewTurn,
    InterviewEvaluation,
    AgentCallLog
)

# Initialize Celery app
celery_app = Celery(
    "datn_workers",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.modules.interviews.tasks",  # Interview AI tasks
        "app.modules.ai.tasks"  # CV analysis AI tasks
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=600,  # 10 minutes max
    task_soft_time_limit=540,  # 9 minutes soft limit
    worker_prefetch_multiplier=1,  # Prefetch one task at a time
    worker_max_tasks_per_child=100,  # Restart worker after 100 tasks
)

# Task routing - DISABLED to use default 'celery' queue
# This avoids queue mismatch issues during development
# celery_app.conf.task_routes = {
#     "app.modules.interviews.tasks.generate_questions_task": {
#         "queue": "questions",
#         "routing_key": "questions.generate"
#     }
# }

if __name__ == "__main__":
    celery_app.start()
