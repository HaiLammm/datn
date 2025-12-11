from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def get_jobs():
    return {"message": "This is the jobs router"}
