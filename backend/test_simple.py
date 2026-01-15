"""Simple test to trigger interview question generation"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.modules.interviews.tasks import generate_questions_task
import uuid

# Use known good IDs from previous successful test
session_id = str(uuid.uuid4())
cv_id = "4314ddc8-61b1-4671-b0d1-f7d291f449e6"  # From logs
user_id = 14  # From logs
job_id = "550e8400-e29b-41d4-a716-446655440000"  # Example

print(f"🚀 Submitting task...")
print(f"   Session ID: {session_id}")
print(f"   CV ID: {cv_id}")
print(f"   User ID: {user_id}")

task = generate_questions_task.delay(
    session_id=session_id,
    cv_id=cv_id,
    job_id=job_id,
    user_id=user_id,
    num_questions=5
)

print(f"\n✅ Task submitted!")
print(f"   Task ID: {task.id}")
print(f"   Initial state: {task.state}")
print(f"\n⏳ Monitor progress:")
print(f"   tail -f celery_worker.log")
print(f"\n📊 Check status with:")
print(f"   python -c \"from celery.result import AsyncResult; from app.core.celery_app import celery_app; r = AsyncResult('{task.id}', app=celery_app); print(f'State: {{r.state}}, Result: {{r.result}}')\"")
print(f"\n🔍 Query database:")
print(f"   SELECT * FROM interview_sessions WHERE id = '{session_id}'::uuid;")
