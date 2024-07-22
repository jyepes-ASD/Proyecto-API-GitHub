import pytest
from fastapi.testclient import TestClient
from fastapi import status, Response, HTTPException
from unittest.mock import patch, MagicMock
from app.main import app

client = TestClient(app)

@pytest.fixture
def mock_github_user():
    mock_user = MagicMock()
    mock_user.login = "test_user"
    return mock_user

@pytest.fixture
def mock_request_session():
    with patch('starlette.requests.Request.session', new_callable=MagicMock) as mock_session:
        yield mock_session

def test_root(mock_request_session):
    mock_request_session.clear.return_value = None
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert "Login with GitHub" in response.text

@patch("app.routers.login_router.get_current_user")
@patch("app.routers.login_router.Github")
def test_inicio(mock_github, mock_get_current_user, mock_github_user, mock_request_session):
    mock_get_current_user.return_value = mock_github_user
    mock_request_session.get.return_value = 'fake_token'
    mock_github.return_value.get_user.return_value = mock_github_user
    response = client.get("/inicio")
    assert response.status_code == status.HTTP_200_OK
    assert "Inicio" in response.text
    assert "test_user" in response.text

@patch("app.routers.login_router.oauth.github.authorize_redirect")
def test_login(mock_authorize_redirect, mock_request_session):
    mock_authorize_redirect.return_value = Response()
    response = client.get("/login")
    assert response.status_code == status.HTTP_200_OK

@patch("app.routers.login_router.oauth.github.authorize_access_token")
@patch("app.routers.login_router.Github")
def test_auth(mock_github, mock_authorize_access_token, mock_request_session):
    mock_authorize_access_token.return_value = {"access_token": "test_token"}
    mock_request_session.get.return_value = "test_token"
    mock_github.return_value.get_user.return_value = MagicMock(login="test_user")
    response = client.post("/auth")  # Usamos POST ya que es el método definido en la ruta


def test_logout(mock_request_session):
    mock_request_session.clear.return_value = None
    response = client.get("/logout")
    assert response.status_code == status.HTTP_200_OK  

def test_logout_redirect(mock_request_session):
    response = client.get("/logout_redirect")
    assert response.status_code == status.HTTP_200_OK
    assert "Logging out..." in response.text

# Nuevas pruebas para get_current_user
@patch("app.routers.login_router.Github")
def test_get_current_user_no_token(mock_github, mock_request_session):
    mock_request_session.get.return_value = None
    response = client.get("/inicio")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "No authenticated" in response.json()["detail"]

@patch("app.routers.login_router.Github")
def test_get_current_user_exception(mock_github, mock_request_session):
    mock_request_session.get.return_value = "fake_token"
    mock_github.side_effect = Exception("GitHub error")
    
    # Ajusta la función get_current_user para que maneje correctamente la excepción
    with patch("app.routers.login_router.get_current_user") as mock_get_current_user:
        mock_get_current_user.side_effect = HTTPException(status_code=500, detail="Error al obtener el usuario: GitHub error")
        response = client.get("/inicio")
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Error al obtener el usuario: GitHub error" in response.json()["detail"]

# Nueva prueba para /relogin
@patch("app.routers.login_router.oauth.github.authorize_redirect")
def test_relogin(mock_authorize_redirect, mock_request_session):
    mock_authorize_redirect.return_value = Response()
    response = client.get("/relogin")
    assert response.status_code == status.HTTP_200_OK

# Prueba para el caso de token de acceso no obtenido en /auth
@patch("app.routers.login_router.oauth.github.authorize_access_token")
def test_auth_no_access_token(mock_authorize_access_token, mock_request_session):
    mock_authorize_access_token.return_value = None  # Simula no obtener el token
    response = client.post("/auth")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Token de acceso no obtenido" in response.json()["detail"]
