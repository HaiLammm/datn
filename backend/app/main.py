from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

# CORS: allow frontend to connect
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import all models at startup to ensure SQLAlchemy relationships are resolved
@app.on_event("startup")
async def startup_event():
    """Import all models to register them with SQLAlchemy."""
    try:
        # Import models in dependency order
        from app.modules.users.models import User  # noqa: F401
        from app.modules.jobs.models import JobDescription  # noqa: F401
        from app.modules.cv.models import CV  # noqa: F401
        from app.modules.interviews.models import (  # noqa: F401
            InterviewSession,
            InterviewQuestion,
            InterviewTurn,
            InterviewEvaluation,
            AgentCallLog
        )
    except Exception as e:
        print(f"Warning: Could not import all models: {e}")

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def read_root():
    return {"message": "Welcome to the API"}
