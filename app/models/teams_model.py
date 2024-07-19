from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel


class Member(BaseModel):
    id: int
    login: str
   
class Team(BaseModel):
    id: int
    name: str
    members_count: int
    members: List[Member]
 
class TeamsResponse(BaseModel):
    total_teams: int
    teams: list[Team]