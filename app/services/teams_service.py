from typing import List
from datetime import datetime, timedelta
from fastapi import HTTPException, APIRouter
from github import Github
from token_1 import my_git
from app.models.teams_model import TeamsResponse, Team, Member

teams_router = APIRouter()

class TeamsService:

    def __init__(self):
        self.github_client = my_git

    def get_teams(self, org_name: str) -> TeamsResponse:
        try:
            org = self.github_client.get_organization(org_name)
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

# Crear una instancia del servicio
teams_service = TeamsService()

@teams_router.get("/orgs/{org_name}/teams", response_model=TeamsResponse)
def get_teams(org_name: str):
    """
    Obtiene todos los equipos de una organización en GitHub.
    Args:
        org_name (str): El nombre de la organización.
    Returns:
        TeamsResponse: Una respuesta con la lista de equipos y sus detalles.
    """
    try:
        return teams_service.get_teams(org_name)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener los equipos: {str(e)}")
