import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from faker import Faker
from fastapi import HTTPException
from routers.user_router import get_statistics_of_users, get_user_events, perfil_info
from models.user_model import UsersStats, UserStats, Event

fake = Faker()

# Funciones Mock

class MockOwner:
    def __init__(self, login):
        self.login = login

class MockRepository:
    def __init__(self, owner_login, languages):
        self.owner = MockOwner(owner_login)
        self.name = fake.word()
        self.created_at = datetime.now()
        self.languages = languages

    def get_languages(self):
        return self.languages

    def get_pulls(self):
        return [MagicMock(created_at=datetime.now()) for _ in range(fake.random_int(0, 5))]

    def get_issues(self):
        return [MagicMock(created_at=datetime.now()) for _ in range(fake.random_int(0, 5))]

    def get_commits(self):
        return [MagicMock(commit=MagicMock(author=MagicMock(date=datetime.now()))) for _ in range(fake.random_int(0, 10))]

def generate_mock_repos_with_languages(num_repos, languages):
    return [MockRepository(fake.user_name(), languages) for _ in range(num_repos)]

# Pruebas para get_statistics_of_users

def test_get_statistics_of_users():
    with patch('routers.user_router.user.get_repos', return_value=generate_mock_repos_with_languages(5, {"Python": 1000, "JavaScript": 2000})):
        result = get_statistics_of_users()
        assert result is not None
        assert isinstance(result, UsersStats)

def test_get_statistics_of_users_exception():
    with patch('routers.user_router.user.get_repos', side_effect=Exception("Error de prueba")):
        with pytest.raises(HTTPException) as excinfo:
            get_statistics_of_users()
        assert excinfo.value.status_code == 500
        assert "Error al obtener repositorios del usuario" in excinfo.value.detail

def test_get_statistics_of_users_language_accumulation():
    # Primer repositorio con lenguajes iniciales
    repo1_languages = {"Python": 1000, "JavaScript": 2000}
    # Segundo repositorio con los mismos lenguajes para provocar la acumulación
    repo2_languages = {"Python": 500, "JavaScript": 1500}
    mock_repos = [
        MockRepository("user1", repo1_languages),
        MockRepository("user1", repo2_languages)
    ]

    with patch('routers.user_router.user.get_repos', return_value=mock_repos):
        result = get_statistics_of_users()
        assert result is not None
        assert isinstance(result, UsersStats)
        user_stats = result.users_statistics

        total_python_bytes = repo1_languages["Python"] + repo2_languages["Python"]
        total_javascript_bytes = repo1_languages["JavaScript"] + repo2_languages["JavaScript"]
        total_bytes = total_python_bytes + total_javascript_bytes

        expected_python_percentage = f"{(total_python_bytes / total_bytes) * 100:.2f}%"
        expected_javascript_percentage = f"{(total_javascript_bytes / total_bytes) * 100:.2f}%"

        assert user_stats["user1"].languages["Python"] == expected_python_percentage
        assert user_stats["user1"].languages["JavaScript"] == expected_javascript_percentage

def test_get_statistics_of_users_language_exception():
    with patch('routers.user_router.user.get_repos', return_value=generate_mock_repos_with_languages(1, {"Python": 1000})):
        with patch.object(MockRepository, 'get_languages', side_effect=Exception("Error al obtener lenguajes")):
            result = get_statistics_of_users()
            assert result is not None
            assert isinstance(result, UsersStats)

def test_get_statistics_of_users_actions_exception():
    with patch('routers.user_router.user.get_repos', return_value=generate_mock_repos_with_languages(1, {"Python": 1000})):
        with patch.object(MockRepository, 'get_pulls', side_effect=Exception("Error al obtener acciones")):
            result = get_statistics_of_users()
            assert result is not None
            assert isinstance(result, UsersStats)

# Funciones Mock para get_user_events

class MockRepositories:
    def __init__(self, name):
        self.name = name

    def get_events(self):
        return [
            MagicMock(
                type="PushEvent",
                repo=self,
                created_at=fake.date_time_this_month(),
                public=True,
                org=None
            ),
            MagicMock(
                type="PullRequestEvent",
                repo=self,
                created_at=fake.date_time_this_month(),
                public=False,
                org=None
            )
        ]

class MockGithubUser:
    def __init__(self):
        self.disk_usage = fake.random_int(1024, 2048)

    def get_repos(self):
        num_repos = fake.random_int(1, 5)
        return [MockRepositories(fake.word()) for _ in range(num_repos)]

def test_get_user_events():
    mock_user = MockGithubUser()

    with patch('routers.user_router.get_current_user', return_value=mock_user):
        result = get_user_events(user=mock_user)
        assert result is not None
        assert isinstance(result, list)
        for event in result:
            assert isinstance(event, Event)

def test_get_user_events_exception():
    with patch('routers.user_router.get_current_user', side_effect=Exception("Error de prueba")):
        with pytest.raises(HTTPException) as excinfo:
            get_user_events()
        assert excinfo.value.status_code == 500
        assert "Error al obtener eventos del usuario" in excinfo.value.detail

def test_get_user_events_repo_exception():
    mock_user = MockGithubUser()

    with patch('routers.user_router.get_current_user', return_value=mock_user):
        with patch.object(MockRepositories, 'get_events', side_effect=Exception("Error al obtener eventos")):
            result = get_user_events(user=mock_user)
            assert result is not None
            assert isinstance(result, list)

# Funciones Mock para perfil_info

class MockGithubUsers:
    def __init__(self):
        self.login = "mock_user"
        self.name = "Mock User"
        self.avatar_url = "https://example.com/avatar"
        self.bio = "Mock bio"
        self.location = "Mock location"
        self.blog = "https://example.com/blog"
        self.email = "mock@example.com"
        self.public_repos = 10
        self.created_at = datetime(2023, 1, 1)
        self.updated_at = datetime(2023, 1, 2)

def test_perfil_info():
    mock_user = MockGithubUsers()

    with patch('routers.user_router.get_current_user', return_value=mock_user):
        perfil = perfil_info(user=mock_user)
        assert perfil["login"] == mock_user.login
        assert perfil["nombre"] == mock_user.name
        assert perfil["avatar_url"] == mock_user.avatar_url
        assert perfil["bio"] == mock_user.bio
        assert perfil["ubicacion"] == mock_user.location
        assert perfil["blog"] == mock_user.blog
        assert perfil["email"] == mock_user.email
        assert perfil["public_repos"] == mock_user.public_repos
        assert perfil["creacion"] == mock_user.created_at
        assert perfil["actualizacion"] == mock_user.updated_at

def test_perfil_info_exception():
    with patch('routers.user_router.get_current_user', side_effect=Exception("Error de prueba")):
        with pytest.raises(HTTPException) as excinfo:
            perfil_info()
        assert excinfo.value.status_code == 500
        assert "Error al obtener la información del perfil" in excinfo.value.detail

if __name__ == "__main__":
    pytest.main()
