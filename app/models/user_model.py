from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel



'''
class Users(BaseModel):
    username: set
    # repositories: list
    # repositories: int
    # mainlanguage: str
    # # rank: int
'''


class UserStats(BaseModel):
    repos_count: int
    languages: Dict[str, str]
    actions_per_day: int

class UsersStats(BaseModel):
    users_statistics: Dict[str, UserStats]

class Event(BaseModel):
    type: str
    repo: str
    date: str
    public: bool
    org: Optional[str]
    disk: Optional[int]


class User(BaseModel):
    username: str
    fullname: str
    email: str
    repositories: list
    actionshistory: list
    actionscontributions: list
    usedlanguages: list 
    teams: list

# class UserStats(BaseModel):
#     repositories: int
#     actionsday: int
#     contributionsrepositories: int
#     usedlanguages: int
#     teams: int