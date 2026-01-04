from fastapi import APIRouter
from app.modules.auth.router import router as auth_router
from app.modules.jobs.router import router as jobs_router
from app.modules.cv.router import router as cv_router
from app.modules.users.router import router as users_router
from app.modules.ai.router import router as ai_router
from app.modules.admin.router import router as admin_router
from app.modules.messages.router import router as messages_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(jobs_router, prefix="/jobs", tags=["jobs"])
api_router.include_router(cv_router, prefix="/cvs", tags=["cvs"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(ai_router, prefix="/ai", tags=["ai"])
api_router.include_router(admin_router, prefix="/admin", tags=["admin"])
api_router.include_router(messages_router, prefix="/messages", tags=["messages"])
