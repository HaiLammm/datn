from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def get_cvs():
    return {"message": "This is the cvs router"}
