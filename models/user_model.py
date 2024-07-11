from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel




class Users(BaseModel):
    username: set
    # repositories: list
    # repositories: int
    # mainlanguage: str
    # # rank: int



class UsersStats(BaseModel):
    toprank: list
    languages: list




class User(BaseModel):
    username: str
    fullname: str
    email: str
    repositories: list
    actionshistory: list
    actionscontributions: list
    usedlanguages: list 
    teams: list

class UserStats(BaseModel):
    repositories: int
    actionsday: int
    contributionsrepositories: int
    usedlanguages: int
    teams: int
