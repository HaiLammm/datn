# Test sending interview question generation task
from app.modules.interviews.tasks import generate_questions_task

task = generate_questions_task.delay(
    session_id='56400bcb-bd32-4587-9d0d-f71ebd5cf008',
    job_description='Python Backend Developer with 3+ years experience in FastAPI and SQLAlchemy',
    cv_id='4314ddc8-61b1-4671-b0d1-f7d291f449e6',
    user_id=5,
    position_level='middle',
    num_questions=10,
    focus_areas=['python', 'fastapi', 'sqlalchemy']
)

print(f'✅ Task sent successfully!')
print(f'Task ID: {task.id}')
print(f'Initial status: {task.status}')
print('\nMonitor progress:')
print('  - Check celery_worker.log')
print('  - Or query: SELECT status FROM interview_sessions WHERE id = \'56400bcb-bd32-4587-9d0d-f71ebd5cf008\'')
