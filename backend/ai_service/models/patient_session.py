from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class PatientSession(BaseModel):
    patient_id: str
    category: str
    question: str
    answer: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
