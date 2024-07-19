from typing import List
from datetime import datetime
from fastapi import HTTPException, APIRouter, Depends
from github import Github
from token_1 import my_git
from models.user_model import Event, UsersStats
from routers.login_router import get_current_user

user_router = APIRouter()
user = my_git.get_user()
repos = user.get_repos()

@user_router.get("/users/statistics/", response_model=UsersStats)
def get_statistics_of_users():
    try:
        user_stats = {}

        try:
            repos = user.get_repos()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al obtener repositorios del usuario: {e}")

        for repository in repos:
            owner = repository.owner.login
            if owner not in user_stats:
                user_stats[owner] = {
                    "repos_count": 0,
                    "languages": {},
                    "actions_per_day": 0,
                }

            user_stats[owner]["repos_count"] += 1

            try:
                langs = repository.get_languages()
                for lang, bytes_count in langs.items():
                    if lang in user_stats[owner]["languages"]:
                        user_stats[owner]["languages"][lang] += bytes_count
                    else:
                        user_stats[owner]["languages"][lang] = bytes_count
            except Exception as e:
                print(f"Error al obtener lenguajes para el repositorio {repository.name}: {e}")

            actions_today = 0
            today = datetime.now().date()
            try:
                actions_today += len([pr for pr in repository.get_pulls() if pr.created_at.date() == today])
                actions_today += len([issue for issue in repository.get_issues() if issue.created_at.date() == today])
                actions_today += len([commit for commit in repository.get_commits() if commit.commit.author.date.date() == today])
            except Exception as e:
                print(f"Error al obtener acciones para el repositorio {repository.name}: {e}")
            user_stats[owner]["actions_per_day"] += actions_today

        for owner, stats in user_stats.items():
            total_bytes = sum(stats["languages"].values())
            stats["languages"] = {lang: f"{(bytes_count / total_bytes) * 100:.2f}%" for lang, bytes_count in stats["languages"].items()}

        return UsersStats(users_statistics=user_stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener estadísticas de usuarios: {e}")

@user_router.get("/users/activity", response_model=List[Event])
def get_user_events(user: Github = Depends(get_current_user)) -> List[Event]:
    try:
        # Obtener eventos del usuario logueado
        events = []
        for repo in user.get_repos():
            try:
                repo_events = repo.get_events()
                events.extend(repo_events)
            except Exception as e:
                # Si el repositorio está vacío o hay otro error, lo omitimos
                print(f"Error obteniendo eventos del repositorio {repo.name}: {e}")

        formatted_events = []

        for event in events:
            formatted_event = {
                "type": event.type,
                "repo": event.repo.name,
                "date": event.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "public": event.public,
                "org": event.org.login if event.org else None,
                "disk": user.disk_usage  # Añadir el campo disk aquí
            }
            # Asegúrate de que cada campo requerido por el modelo Event esté presente
            formatted_events.append(Event(**formatted_event))

        return formatted_events
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener eventos del usuario: {e}")



@user_router.get("/perfil")
def perfil_info(user: Github = Depends(get_current_user)):
    try:
        profile = {
            "login": user.login,
            "nombre": user.name or user.login,
            "avatar_url": user.avatar_url or "no disponible",
            "bio": user.bio or "no disponible",
            "ubicacion": user.location or "no disponible",
            "blog": user.blog or "no disponible",
            "email": user.email or "no disponible",
            "public_repos": user.public_repos,
            "creacion": user.created_at,
            "actualizacion": user.updated_at,
        }
        return profile
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener la información del perfil: {e}")
