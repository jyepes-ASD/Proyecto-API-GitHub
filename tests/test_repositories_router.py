import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.routers.repositories_router import repository_router
from app.models.repository_model import Repository, RepositoriesStats, RepositoryStats, Repositories
from datetime import datetime

app = FastAPI()
app.include_router(repository_router)

@pytest.fixture
def client():
    return TestClient(app)

# Mock data
fake_repositories = [
    Repositories(name="repo1", owner="owner1", state="active", createDate=datetime.now(), lastUseDate=datetime.now()),
    Repositories(name="repo2", owner="owner2", state="inactive", createDate=datetime.now(), lastUseDate=datetime.now())
]
fake_repository_stats = RepositoriesStats(
    repositories=2,
    repositoriesActives=1,
    repositoriesInactives=1,
    prsOpen=10,
    prsClosed=5,
    prsDependabot=2,
    collaborators=4,
    issues=3,
    percentages_languages=["Python 60%", "JavaScript 40%"]
)
fake_repository_detail = Repository(
    name="repo1",
    description="A test repo",
    collaborators=["collab1", "collab2"],
    prsOpen=["PR1", "PR2"],
    prsClosed=["PR3"],
    prsDependabot=["PR4"],
    issuesDetails=["Issue1", "Issue2"],
    branchesDetails=["main", "dev"],
    languagesPercentage=["Python 60%", "JavaScript 40%"]
)
fake_statistics_by_detail = RepositoryStats(
    collaborators=2,
    prsOpen=2,
    prsClosed=1,
    prsDependabot=1,
    issues=2,
    branches=2,
    percentagesLanguages=["Python 60%", "JavaScript 40%"]
)

@patch("app.services.repository_service.RepositoryService.get_repositories")
def test_get_repositories(mock_get_repositories, client):
    mock_get_repositories.return_value = fake_repositories
    response = client.get("/repositories")
    assert response.status_code == 200
    expected_response = [
        {
            "name": repo.name,
            "owner": repo.owner,
            "state": repo.state,
            "createDate": repo.createDate.isoformat() if repo.createDate else None,
            "lastUseDate": repo.lastUseDate.isoformat() if repo.lastUseDate else None
        }
        for repo in fake_repositories
    ]
    actual_response = response.json()
    assert actual_response == expected_response

@patch("app.services.repository_service.RepositoryService.get_statistics_of_repositories")
def test_get_statistics_of_repositories(mock_get_statistics_of_repositories, client):
    mock_get_statistics_of_repositories.return_value = fake_repository_stats
    response = client.get("/repositories/statistics")
    assert response.status_code == 200
    assert response.json() == fake_repository_stats.model_dump()

@patch("app.services.repository_service.RepositoryService.get_repository_detail")
def test_get_repository_detail(mock_get_repository_detail, client):
    mock_get_repository_detail.return_value = fake_repository_detail
    response = client.get("/repository/repo1")
    assert response.status_code == 200
    assert response.json() == fake_repository_detail.model_dump()

@patch("app.services.repository_service.RepositoryService.get_statistics_by_detail")
def test_get_statistics_by_detail(mock_get_statistics_by_detail, client):
    mock_get_statistics_by_detail.return_value = fake_statistics_by_detail
    response = client.get("/repository/repo1/statistics")
    assert response.status_code == 200
    assert response.json() == fake_statistics_by_detail.model_dump()

# Pruebas de excepciones
@patch("app.services.repository_service.RepositoryService.get_repositories")
def test_get_repositories_exception(mock_get_repositories, client):
    mock_get_repositories.side_effect = Exception("Test Exception")
    response = client.get("/repositories")
    assert response.status_code == 500
    assert response.json() == {"detail": "Error al obtener repositorios: Test Exception"}

@patch("app.services.repository_service.RepositoryService.get_statistics_of_repositories")
def test_get_statistics_of_repositories_exception(mock_get_statistics_of_repositories, client):
    mock_get_statistics_of_repositories.side_effect = Exception("Test Exception")
    response = client.get("/repositories/statistics")
    assert response.status_code == 500
    assert response.json() == {"detail": "Error al obtener estadísticas de los repositorios: Test Exception"}

@patch("app.services.repository_service.RepositoryService.get_repository_detail")
def test_get_repository_detail_exception(mock_get_repository_detail, client):
    mock_get_repository_detail.side_effect = Exception("Test Exception")
    response = client.get("/repository/repo1")
    assert response.status_code == 500
    assert response.json() == {"detail": "Error al obtener detalles del repositorio: Test Exception"}

@patch("app.services.repository_service.RepositoryService.get_statistics_by_detail")
def test_get_statistics_by_detail_exception(mock_get_statistics_by_detail, client):
    mock_get_statistics_by_detail.side_effect = Exception("Test Exception")
    response = client.get("/repository/repo1/statistics")
    assert response.status_code == 500
    assert response.json() == {"detail": "Error al obtener estadísticas detalladas del repositorio: Test Exception"}
