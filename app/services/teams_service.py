from typing import List
from datetime import datetime, timedelta
from fastapi import HTTPException, APIRouter
from github import Github
from token_1 import my_git
from app.models.teams_model import TeamsResponse, Team, Member
import os
from dotenv import load_dotenv

load_dotenv()

ORG_NAME = os.getenv("ORG_NAME")

teams_router = APIRouter()

class TeamsService:

    def __init__(self):
        self.github_client = my_git

    def get_teams(self) -> TeamsResponse:
        try:
            org = self.github_client.get_organization(ORG_NAME)
            teams = org.get_teams()
            teams_list = []

            for team in teams:
                members = team.get_members()
                members_list = [Member(id=member.id, login=member.login) for member in members]
                members_count = len(members_list)
                teams_list.append(Team(id=team.id, name=team.name, members_count=members_count, members=members_list))
                
            total_teams = len(teams_list)

            return TeamsResponse(total_teams=total_teams, teams=teams_list)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al obtener los equipos: {e}")

# Crear una instancia del servicio
teams_service = TeamsService()

