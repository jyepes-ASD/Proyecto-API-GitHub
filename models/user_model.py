from pydantic import BaseModel
from typing import Optional

class Event(BaseModel):
    type: str
    repo: str
    date: str
    public: bool
    org: Optional[str]
    disk: Optional[int]