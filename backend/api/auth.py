from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
import models
import dto.user
import utils

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=dto.user.UserOut)
def register(user_in: dto.user.UserCreate, db: Session = Depends(get_db)):
    user_exist = db.query(models.User).filter(
        models.User.email == user_in.email).first()
    if user_exist:
        raise HTTPException(status=400, detail="Email invalid")
    hashed_pwd = utils.hash_password(user_in.password)
    new_user = models.User(email=user_in.email,
                           user_name=user_in.user_name, hashed_pwd=hashed_pwd)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


router.post("/login", response_model=dto.user.Token)


def login(user_credentials: dto.user.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(
        models.User.email == user_credentials).first()
    if not user or not utils.verify_password(user_credentials.password, user.hashed_pwd):
        raise HTTPException("User name or password is incorrect")
    access_token = utils.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}
