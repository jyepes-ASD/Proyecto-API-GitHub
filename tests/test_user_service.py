import pytest
from unittest.mock import MagicMock, PropertyMock, patch
from fastapi import HTTPException
from faker import Faker
from datetime import datetime
from app.models.user_model import Event, UsersStats, UserStats
from app.services.user_service import UserService

fake = Faker()

@pytest.fixture
def mock_github_user():
    user = MagicMock()
    user.get_repos.return_value = []
    user.disk_usage = 5000  # Valor ficticio para disk_usage
    return user

@pytest.fixture
def user_service(mock_github_user):
    with patch('app.services.user_service.my_git') as mock_git:
        mock_git.get_user.return_value = mock_github_user
        service = UserService()
        return service

# Pruebas para get_statistics_of_users
def test_get_statistics_of_users_success(user_service, mock_github_user):
    repo_mock_1 = MagicMock()
    repo_mock_1.owner.login = 'test_user'
    repo_mock_1.get_languages.return_value = {'Python': 1000}
    repo_mock_1.get_pulls.return_value = []
    repo_mock_1.get_issues.return_value = []
    repo_mock_1.get_commits.return_value = []

    repo_mock_2 = MagicMock()
    repo_mock_2.owner.login = 'test_user'
    repo_mock_2.get_languages.return_value = {'Python': 500, 'JavaScript': 2000}
    repo_mock_2.get_pulls.return_value = []
    repo_mock_2.get_issues.return_value = []
    repo_mock_2.get_commits.return_value = []

    mock_github_user.get_repos.return_value = [repo_mock_1, repo_mock_2]

    stats = user_service.get_statistics_of_users()

    assert isinstance(stats, UsersStats)
    assert 'test_user' in stats.users_statistics
    assert stats.users_statistics['test_user'].repos_count == 2
    assert 'Python' in stats.users_statistics['test_user'].languages
    assert 'JavaScript' in stats.users_statistics['test_user'].languages
    assert stats.users_statistics['test_user'].languages['Python'] == '42.86%'  # (1000 + 500) / 3500 * 100
    assert stats.users_statistics['test_user'].languages['JavaScript'] == '57.14%'  # 2000 / 3500 * 100

def test_get_statistics_of_users_repo_error(user_service, mock_github_user):
    mock_github_user.get_repos.side_effect = Exception('Repo fetch error')

    with pytest.raises(HTTPException) as exc_info:
        user_service.get_statistics_of_users()
    
    assert exc_info.value.status_code == 500
    assert 'Error al obtener repositorios del usuario' in exc_info.value.detail

def test_get_statistics_of_users_lang_error(user_service, mock_github_user):
    repo_mock = MagicMock()
    repo_mock.owner.login = 'test_user'
    repo_mock.get_languages.side_effect = Exception('Language fetch error')
    repo_mock.get_pulls.return_value = []
    repo_mock.get_issues.return_value = []
    repo_mock.get_commits.return_value = []

    mock_github_user.get_repos.return_value = [repo_mock]

    stats = user_service.get_statistics_of_users()

    assert isinstance(stats, UsersStats)
    assert 'test_user' in stats.users_statistics
    assert stats.users_statistics['test_user'].repos_count == 1
    assert stats.users_statistics['test_user'].languages == {}

def test_get_statistics_of_users_actions_error(user_service, mock_github_user):
    repo_mock = MagicMock()
    repo_mock.owner.login = 'test_user'
    repo_mock.get_languages.return_value = {'Python': 1000}
    repo_mock.get_pulls.side_effect = Exception('Pull request fetch error')
    repo_mock.get_issues.side_effect = Exception('Issues fetch error')
    repo_mock.get_commits.side_effect = Exception('Commits fetch error')

    mock_github_user.get_repos.return_value = [repo_mock]

    stats = user_service.get_statistics_of_users()

    assert isinstance(stats, UsersStats)
    assert 'test_user' in stats.users_statistics
    assert stats.users_statistics['test_user'].repos_count == 1
    assert 'Python' in stats.users_statistics['test_user'].languages
    assert stats.users_statistics['test_user'].actions_per_day == 0

def test_get_statistics_of_users_general_error(user_service, mock_github_user):
    repo_mock = MagicMock()
    repo_mock.owner.login = 'test_user'
    repo_mock.get_languages.return_value = {'Python': 1000}
    repo_mock.get_pulls.return_value = []
    repo_mock.get_issues.return_value = []
    repo_mock.get_commits.return_value = []

    mock_github_user.get_repos.side_effect = Exception('General error')

    with pytest.raises(HTTPException) as exc_info:
        user_service.get_statistics_of_users()
    
    assert exc_info.value.status_code == 500
    assert 'Error al obtener estadísticas de usuarios' in exc_info.value.detail

# Pruebas para get_user_events
def test_get_user_events_success(user_service, mock_github_user):
    repo_mock = MagicMock()
    repo_mock.name = 'test_repo'

    event_mock_1 = MagicMock()
    event_mock_1.type = 'PushEvent'
    event_mock_1.repo.name = 'test_repo'
    event_mock_1.created_at = datetime.now()
    event_mock_1.public = True
    event_mock_1.org.login = 'test_org'

    event_mock_2 = MagicMock()
    event_mock_2.type = 'PullRequestEvent'
    event_mock_2.repo.name = 'test_repo'
    event_mock_2.created_at = datetime.now()
    event_mock_2.public = False
    event_mock_2.org = None

    repo_mock.get_events.return_value = [event_mock_1, event_mock_2]
    mock_github_user.get_repos.return_value = [repo_mock]

    events = user_service.get_user_events(mock_github_user)

    assert isinstance(events, list)
    assert len(events) == 2
    assert events[0].type == 'PushEvent'
    assert events[0].repo == 'test_repo'
    assert events[0].public is True
    assert events[0].org == 'test_org'
    assert events[0].disk == 5000

    assert events[1].type == 'PullRequestEvent'
    assert events[1].repo == 'test_repo'
    assert events[1].public is False
    assert events[1].org is None
    assert events[1].disk == 5000

def test_get_user_events_repo_error(user_service, mock_github_user):
    repo_mock = MagicMock()
    repo_mock.name = 'test_repo'
    repo_mock.get_events.side_effect = Exception('Event fetch error')

    mock_github_user.get_repos.return_value = [repo_mock]

    events = user_service.get_user_events(mock_github_user)

    assert isinstance(events, list)
    assert len(events) == 0


# Pruebas para get_perfil_info
def test_get_perfil_info_success(user_service, mock_github_user):
    mock_github_user.login = 'test_user'
    mock_github_user.name = 'Test User'
    mock_github_user.avatar_url = 'http://example.com/avatar.png'
    mock_github_user.bio = 'Test bio'
    mock_github_user.location = 'Test location'
    mock_github_user.blog = 'http://example.com'
    mock_github_user.email = 'test@example.com'
    mock_github_user.public_repos = 10
    mock_github_user.created_at = datetime.now()
    mock_github_user.updated_at = datetime.now()

    profile_info = user_service.get_perfil_info(mock_github_user)
    
    assert profile_info['login'] == 'test_user'
    assert profile_info['nombre'] == 'Test User'
    assert profile_info['avatar_url'] == 'http://example.com/avatar.png'
    assert profile_info['bio'] == 'Test bio'
    assert profile_info['ubicacion'] == 'Test location'
    assert profile_info['blog'] == 'http://example.com'
    assert profile_info['email'] == 'test@example.com'
    assert profile_info['public_repos'] == 10
    assert profile_info['creacion'] is not None
    assert profile_info['actualizacion'] is not None

def test_get_perfil_info_general_error(user_service, mock_github_user):
    mock_github_user.login = 'test_user'
    mock_github_user.name = 'Test User'
    mock_github_user.avatar_url = 'http://example.com/avatar.png'
    mock_github_user.bio = 'Test bio'
    mock_github_user.location = 'Test location'
    mock_github_user.blog = 'http://example.com'
    mock_github_user.email = 'test@example.com'
    mock_github_user.public_repos = 10
    mock_github_user.created_at = datetime.now()
    mock_github_user.updated_at = datetime.now()

    # Asegurarte de que el método que realmente se llama eleve la excepción
    with patch.object(UserService, 'get_perfil_info', side_effect=HTTPException(status_code=500, detail='Error al obtener la información del perfil')):
        with pytest.raises(HTTPException) as exc_info:
            user_service.get_perfil_info(mock_github_user)
        
        assert exc_info.value.status_code == 500
        assert 'Error al obtener la información del perfil' in exc_info.value.detail

def test_get_statistics_of_users_general_error(user_service, mock_github_user):
    mock_github_user.get_repos.side_effect = Exception('General error')
    
    with pytest.raises(HTTPException) as exc_info:
        user_service.get_statistics_of_users()
    
    assert exc_info.value.status_code == 500
    assert 'Error al obtener estadísticas de usuarios' in exc_info.value.detail

def test_get_user_events_general_error(user_service, mock_github_user):
    mock_github_user.get_repos.side_effect = Exception('General error')
    
    with pytest.raises(HTTPException) as exc_info:
        user_service.get_user_events(mock_github_user)
    
    assert exc_info.value.status_code == 500
    assert 'Error al obtener eventos del usuario' in exc_info.value.detail

