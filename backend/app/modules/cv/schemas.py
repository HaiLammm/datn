import uuid
from datetime import datetime

from pydantic import BaseModel


class CVBase(BaseModel):
    filename: str


class CVCreate(CVBase):
    user_id: int
    file_path: str


class CVResponse(CVBase):
    id: uuid.UUID
    user_id: int
    file_path: str
    uploaded_at: datetime
    is_active: bool

    class Config:
        from_attributes = True

