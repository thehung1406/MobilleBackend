# app/schemas/common.py
from pydantic import BaseModel

class TaskResponse(BaseModel):
    message: str
    task_id: str
    status: str
