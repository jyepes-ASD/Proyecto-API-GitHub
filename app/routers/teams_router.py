from typing import List
from fastapi import APIRouter, HTTPException
from app.services.teams_service import TeamsService, teams_service
from app.models.teams_model import TeamsResponse

teams_router = APIRouter()

@teams_router.get("/orgs/teams", response_model=TeamsResponse)
def get_teams():
    """
    Obtiene todos los equipos de una organización en GitHub.
    Args:
        org_name (str): El nombre de la organización.
    Returns:
        TeamsResponse: Una respuesta con la lista de equipos y sus detalles.
    """
    try:
        return teams_service.get_teams()
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener los equipos: {str(e)}")
