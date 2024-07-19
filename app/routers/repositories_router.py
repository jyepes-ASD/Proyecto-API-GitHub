from typing import List
from fastapi import APIRouter, HTTPException
from app.services.repository_service import RepositoryService
from app.models.repository_model import Repository, RepositoriesStats, RepositoryStats, Repositories

repository_router = APIRouter()
repository_service = RepositoryService()

@repository_router.get("/repositories", response_model=List[Repositories])
def get_repositories():
    """
    Trae todos los repositorios desde Github.
    Returns: Lista con todos los repositorios con algunos de sus respectivos detalles.
    """
    try:
        repositories = repository_service.get_repositories()
        return repositories
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener repositorios: {str(e)}")

@repository_router.get("/repositories/statistics", response_model=RepositoriesStats)
def get_statistics_of_repositories():
    try:
        repository_statics = repository_service.get_statistics_of_repositories()
        return repository_statics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener estadísticas de los repositorios: {str(e)}")

@repository_router.get("/repository/{repo_name}", response_model=Repository)
def get_repository_detail(repo_name: str):
    try:
        repository_detail = repository_service.get_repository_detail(repo_name)
        return repository_detail
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener detalles del repositorio: {str(e)}")

@repository_router.get("/repository/{repo_name}/statistics", response_model=RepositoryStats)
def get_statistics_by_detail(repo_name: str):
    try:
        statistics_by_detail = repository_service.get_statistics_by_detail(repo_name)
        return statistics_by_detail
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener estadísticas detalladas del repositorio: {str(e)}")
