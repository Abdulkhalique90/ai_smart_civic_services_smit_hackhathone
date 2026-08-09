from pydantic import BaseModel
from typing import Optional


class ComplaintCreate(BaseModel):
    description: str
    location: Optional[str] = None


class ComplaintUpdate(BaseModel):
    status: Optional[str] = None
    assigned_department: Optional[str] = None
    location: Optional[str] = None


class ComplaintOut(BaseModel):
    complaint_id: int
    description: str
    category: Optional[str]
    priority: Optional[str]
    location: Optional[str]
    date: str
    status: str
    assigned_department: Optional[str]
    recommended_department: Optional[str]
    ai_output: Optional[str]
    resolved_date: Optional[str]
