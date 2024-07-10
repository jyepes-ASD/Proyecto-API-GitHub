from typing import List
from datetime import datetime, timedelta
from fastapi import HTTPException, Request, APIRouter, Path, Query,Depends
from fastapi.responses import HTMLResponse, JSONResponse
from github import Github
import os
from token_1 import my_git
from router.login_router import get_current_user
from datetime import datetime, timedelta
from models.repository_model import (
                                         Repositories,
                                         RepositoriesStats,
                                         Repository,
                                         RepositoryStats,)

user_router = APIRouter()


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

def get_user_repos(self, username):# trae el nombre del repositorio segun la busqueda y se complementa con con la funcion get_pull_request
    user = self.client.get_user(username)
    repos = user.get_repos()
    repos_with_pulls = []
    for repo in repos:
        pulls = self.get_pull_requests(repo)
        repo_data = {
            "name": repo.name,#nombre del repositorio
            "full_name": repo.full_name,#usuario y repositorio
            "pulls": pulls# si tiene o no PR
        }
        repos_with_pulls.append(repo_data)
    return repos_with_pulls

def get_pull_requests(self, repo):#funcion para traer PR
    pulls = repo.get_pulls(state='open')
    return [{"title": pull.title, "html_url": pull.html_url} for pull in pulls]

def get_user_events(self, username):#funcion del historial de eventos o accion por usuario
    user = self.client.get_user(username)
    events = user.get_events()
    formatted_events = []
    for event in events:
        formatted_event = {
            "type": event.type,#tipo de evento o accion
            "repo": event.repo.name,#nombre del usuario y en donde se hizo la accion
            "date": event.created_at.strftime("%d/%m/%Y %H:%M:%S"),#fecha del evento o accion
            "public": event.public,#si es publico o no
            "org": event.org.login if event.org else None,# si tiene una organizacion de codigo en lo cual hizo la accion
            "disk": event.actor.disk_usage# el numero de bytes que uso en maquina al hacer esa accion
        }
        formatted_events.append(formatted_event)
    return formatted_events
'''
def get_github_service():#funcion que verifica el token proporcionado
    token = os.getenv("GITHUB_TOKEN")#TOKEN ya enviado por consola
    if not token:
        raise HTTPException(status_code=400, detail="GitHub token not provided")#mensaje de error
    return GitHubService(token)
   
@user_router.get("/users/{username}/repos")#parate para buscar los repositorios
async def get_user_repos(username: str, github_service: GitHubService = Depends(get_github_service)):
    try:
        repos = github_service.get_user_repos(username)
        return JSONResponse(content={"repos": repos})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
 '''
@user_router.get("/users/activity")#parte para consultar la actividad del usuario
def get_user_activity(user: Github = Depends(get_current_user)):
    events = user.get_events()
    print(events)
    formatted_events = []
    for event in events:
        formatted_event = {
            "type": event.type,#tipo de evento o accion
            "repo": event.repo.name,#nombre del usuario y en donde se hizo la accion
            "date": event.created_at.strftime("%d/%m/%Y %H:%M:%S"),#fecha del evento o accion
            "public": event.public,#si es publico o no
            "org": event.org.login if event.org else None,# si tiene una organizacion de codigo en lo cual hizo la accion
            "disk": event.actor.disk_usage# el numero de bytes que uso en maquina al hacer esa accion
        }
        formatted_events.append(formatted_event)
    return formatted_events


