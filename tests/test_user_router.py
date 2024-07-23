import pytest
from fastapi import FastAPI, HTTPException, Depends
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from starlette.middleware.sessions import SessionMiddleware
from github import Github
from app.routers.login_router import get_current_user
from app.routers.user_router import user_router
from app.models.user_model import Event, UsersStats, UserStats
from app.services.user_service import user_service

app = FastAPI()
app.include_router(user_router)
app.add_middleware(SessionMiddleware, secret_key="secret-key")  # Agregar SessionMiddleware

@pytest.fixture
def client():
    return TestClient(app)

# Mock data
fake_user_stats = UserStats(
    repos_count=10,
    languages={"Python": "60%", "JavaScript": "40%"},
    actions_per_day=5
)
fake_users_stats = UsersStats(
    users_statistics={
        "user1": fake_user_stats,
        "user2": fake_user_stats
    }
)
fake_events = [
    Event(type="PushEvent", repo="repo1", date="2023-07-21T15:54:13Z", public=True, org="org1", disk=100),
    Event(type="PullRequestEvent", repo="repo2", date="2023-07-20T12:34:56Z", public=False, org="org2", disk=200)
]
fake_profile_info = {
    "login": "testuser",
    "id": 12345,
    "name": "Test User",
    "email": "testuser@example.com"
}

# Helper function to mock current user
def mock_get_current_user():
    user = MagicMock(spec=Github)
    user.get_user.return_value = MagicMock(login="testuser")
    return user

def override_get_current_user():
    return mock_get_current_user()

app.dependency_overrides[get_current_user] = override_get_current_user

@patch("app.services.user_service.user_service.get_statistics_of_users")
def test_get_statistics_of_users(mock_get_statistics_of_users, client):
    mock_get_statistics_of_users.return_value = fake_users_stats
    response = client.get("/users/statistics/")
    assert response.status_code == 200
    assert response.json() == fake_users_stats.model_dump()

@patch("app.services.user_service.user_service.get_user_events")
def test_get_user_events(mock_get_user_events, client):
    mock_get_user_events.return_value = fake_events
    response = client.get("/users/activity")
    assert response.status_code == 200
    assert response.json() == [event.model_dump() for event in fake_events]

@patch("app.services.user_service.user_service.get_perfil_info")
def test_perfil_info(mock_get_perfil_info, client):
    mock_get_perfil_info.return_value = fake_profile_info
    response = client.get("/perfil")
    assert response.status_code == 200
    assert response.json() == fake_profile_info

# Pruebas de excepciones
@patch("app.services.user_service.user_service.get_statistics_of_users")
def test_get_statistics_of_users_exception(mock_get_statistics_of_users, client):
    mock_get_statistics_of_users.side_effect = HTTPException(status_code=400, detail="Test HTTPException")
    response = client.get("/users/statistics/")
    assert response.status_code == 400
    assert response.json() == {"detail": "Test HTTPException"}

@patch("app.services.user_service.user_service.get_statistics_of_users")
def test_get_statistics_of_users_general_exception(mock_get_statistics_of_users, client):
    mock_get_statistics_of_users.side_effect = Exception("Test General Exception")
    response = client.get("/users/statistics/")
    assert response.status_code == 500
    assert response.json() == {"detail": "Error al obtener estadísticas de usuarios: Test General Exception"}

@patch("app.services.user_service.user_service.get_user_events")
def test_get_user_events_http_exception(mock_get_user_events, client):
    mock_get_user_events.side_effect = HTTPException(status_code=400, detail="Test HTTPException")
    response = client.get("/users/activity")
    assert response.status_code == 400
    assert response.json() == {"detail": "Test HTTPException"}

@patch("app.services.user_service.user_service.get_user_events")
def test_get_user_events_general_exception(mock_get_user_events, client):
    mock_get_user_events.side_effect = Exception("Test General Exception")
    response = client.get("/users/activity")
    assert response.status_code == 500
    assert response.json() == {"detail": "Error al obtener eventos del usuario: Test General Exception"}

@patch("app.services.user_service.user_service.get_perfil_info")
def test_perfil_info_http_exception(mock_get_perfil_info, client):
    mock_get_perfil_info.side_effect = HTTPException(status_code=400, detail="Test HTTPException")
    response = client.get("/perfil")
    assert response.status_code == 400
    assert response.json() == {"detail": "Test HTTPException"}

@patch("app.services.user_service.user_service.get_perfil_info")
def test_perfil_info_general_exception(mock_get_perfil_info, client):
    mock_get_perfil_info.side_effect = Exception("Test General Exception")
    response = client.get("/perfil")
    assert response.status_code == 500
    assert response.json() == {"detail": "Error al obtener la información del perfil: Test General Exception"}
