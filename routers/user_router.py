from typing import List
from datetime import datetime, timedelta
from fastapi import HTTPException, Request, APIRouter, Path, Query,Depends
from fastapi.responses import HTMLResponse, JSONResponse
from github import Github
import os
from token_1 import my_git
from routers.login_router import get_current_user
from datetime import datetime, timedelta
from models.user_model import Event
from models.repository_model import (    
                                         Repositories,
                                         RepositoriesStats,
                                         Repository,
                                         RepositoryStats,)

user_router = APIRouter()

@user_router.get("/users/{username}/activity", response_model=List[Event])
def get_user_events(user: Github = Depends(get_current_user)) -> List[Event]:
    events = user.get_events()
    formatted_events = []
    for event in events:
        formatted_event = {
            "type": event.type,
            "repo": event.repo.name,
            "date": event.created_at.strftime("%d/%m/%Y %H:%M:%S"),
            "public": event.public,
            "org": event.org.login if event.org else None,
            "disk": event.actor.disk_usage
            }
        formatted_events.append(Event(**formatted_event))
        return formatted_events


@user_router.get("/perfil")
def perfil_info(user: Github = Depends(get_current_user)):
    profile = {
        "login": user.login ,
        "nombre": user.name or user.login,
        "avatar_url": user.avatar_url or "no disponible",
        "bio": user.bio or "no disponible",
        "ubicacion": user.location or "no disponible",
        "blog": user.blog or "no disponible",
        "email": user.email or "no disponible",
        "public_repos": user.public_repos or "no disponible",
        "creacion": user.created_at,
        "actualizacion": user.updated_at,
    }
    return profile
