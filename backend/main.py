from models import Base
from api import auth
from fastapi import FastAPI
from database import engine

Base.metadata.create_all(bind=engine)
app = FastAPI()
app.include_router(auth.router)


@app.get("/")
def root():
    return {"message": "Hello world"}
