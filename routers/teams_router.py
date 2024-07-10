from typing import List
from datetime import datetime, timedelta
from fastapi import HTTPException, Request, APIRouter, Path, Query
from fastapi.responses import HTMLResponse, JSONResponse
from github import Github
from token_1 import my_git
from datetime import datetime, timedelta
from models.teams_model import(TeamsResponse,
                               Team,
                               Member)


teams_router = APIRouter()


user = my_git.get_user()
repos = user.get_repos()
owner = user.login


@teams_router .get("/orgs/{org_name}/teams", response_model=TeamsResponse)
def get_teams(org_name: str):
    try:
        org = my_git.get_organization(org_name)
        teams = org.get_teams()
        teams_list = []
 
        for team in teams:
            members = team.get_members()
            members_list = [Member(id=member.id, login=member.login) for member in members]
            members_count = len(members_list)
            teams_list.append(Team(id=team.id, name=team.name, members_count=members_count, members=members_list))
 
        return TeamsResponse(teams=teams_list)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener los equipos: {e}")