from typing import List
from fastapi import APIRouter, HTTPException, Depends
from github import Github
from app.services.user_service import user_service
from app.models.user_model import Event, UsersStats
from app.routers.login_router import get_current_user

user_router = APIRouter()

@user_router.get("/users/statistics/", response_model=UsersStats)
def get_statistics_of_users():
    """
    Obtiene estadísticas de los usuarios.
    Returns: UsersStats: Una respuesta con las estadísticas de los usuarios.
    """
    try:
        return user_service.get_statistics_of_users()
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener estadísticas de usuarios: {str(e)}")

@user_router.get("/users/activity", response_model=List[Event])
def get_user_events(user: Github = Depends(get_current_user)) -> List[Event]:
    """
    Obtiene los eventos del usuario logueado.
    Args:
        user (Github): El usuario logueado.
    Returns: List[Event]: Una lista con los eventos del usuario.
    """
    try:
        return user_service.get_user_events(user)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener eventos del usuario: {str(e)}")

@user_router.get("/perfil")
def perfil_info(user: Github = Depends(get_current_user)):
    """
    Obtiene la información del perfil del usuario logueado.
    Args:
        user (Github): El usuario logueado.
    Returns: dict: Un diccionario con la información del perfil del usuario.
    """
    try:
        return user_service.get_perfil_info(user)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener la información del perfil: {str(e)}")
