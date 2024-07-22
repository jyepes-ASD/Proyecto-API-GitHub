import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from datetime import datetime, timedelta
from app.services.repository_service import RepositoryService
from faker import Faker
from app.models.repository_model import Repositories, RepositoriesStats, Repository, RepositoryStats
from typing import Tuple

fake = Faker()

@pytest.fixture
def mock_github_user():
    user = MagicMock()
    repo1 = MagicMock()
    repo1.name = "repo1"
    repo1.owner.login = "owner1"
    repo1.created_at = "2023-01-01"
    repo1.description = "Repository 1 description"
    
    repo2 = MagicMock()
    repo2.name = "repo2"
    repo2.owner.login = "owner2"
    repo2.created_at = "2023-02-01"
    repo2.description = "Repository 2 description"
    
    user.get_repos.return_value = [repo1, repo2]
    return user

@patch('app.services.repository_service.my_git')
def test_get_repositories_from_github(mock_my_git, mock_github_user):
    mock_my_git.get_user.return_value = mock_github_user
    service = RepositoryService()

    repos = service.get_repositories_from_github()
    
    assert len(repos) == 2
    assert repos[0].name == "repo1"
    assert repos[0].owner.login == "owner1"
    assert repos[0].created_at == "2023-01-01"
    assert repos[0].description == "Repository 1 description"
    assert repos[1].name == "repo2"
    assert repos[1].owner.login == "owner2"
    assert repos[1].created_at == "2023-02-01"
    assert repos[1].description == "Repository 2 description"
    mock_my_git.get_user.assert_called_once()
    mock_github_user.get_repos.assert_called_once()

@patch('app.services.repository_service.my_git')
def test_get_repositories_from_github_exception(mock_my_git):
    mock_my_git.get_user.side_effect = Exception("Error al obtener el usuario")
    
    service = RepositoryService()

    with pytest.raises(HTTPException) as exc_info:
        service.get_repositories_from_github()
    
    assert exc_info.value.status_code == 500
    assert str(exc_info.value.detail) == "Error al obtener los repositorios: Error al obtener el usuario"
    
    mock_my_git.get_user.assert_called_once()

@pytest.fixture
def mock_repository():
    repository = MagicMock()
    commit = MagicMock()
    commit.commit.committer.date = datetime.now()
    repository.get_commits.return_value = [commit]
    return repository

@pytest.fixture
def mock_empty_repository():
    repository = MagicMock()
    repository.get_commits.return_value = []
    return repository

@patch('app.services.repository_service.my_git')
def test_get_last_commit_date(mock_my_git, mock_repository):
    service = RepositoryService()
    
    last_commit_date = service.get_last_commit_date(mock_repository)
    
    now = datetime.now()
    # Comparar sólo hasta los segundos
    assert last_commit_date.year == now.year
    assert last_commit_date.month == now.month
    assert last_commit_date.day == now.day
    assert last_commit_date.hour == now.hour
    assert last_commit_date.minute == now.minute
    assert last_commit_date.second == now.second
    mock_repository.get_commits.assert_called_once()

@patch('app.services.repository_service.my_git')
def test_get_last_commit_date_no_commits(mock_my_git, mock_empty_repository):
    service = RepositoryService()
    
    last_commit_date = service.get_last_commit_date(mock_empty_repository)
    
    assert last_commit_date is None
    mock_empty_repository.get_commits.assert_called_once()

@patch('app.services.repository_service.my_git')
def test_get_last_commit_date_exception(mock_my_git, mock_repository):
    mock_repository.get_commits.side_effect = Exception("Error al obtener commits")
    
    service = RepositoryService()
    
    last_commit_date = service.get_last_commit_date(mock_repository)
    
    assert last_commit_date is None
    mock_repository.get_commits.assert_called_once()

# Pruebas adicionales para get_repository_state
@patch('app.services.repository_service.RepositoryService.get_last_commit_date')
def test_get_repository_state_active(mock_get_last_commit_date):
    mock_get_last_commit_date.return_value = datetime.now()
    service = RepositoryService()
    repository = MagicMock()

    state = service.get_repository_state(repository)
    
    assert state == "Activo"

@patch('app.services.repository_service.RepositoryService.get_last_commit_date')
def test_get_repository_state_inactive(mock_get_last_commit_date):
    mock_get_last_commit_date.return_value = datetime.now() - timedelta(days=180)  # 6 months ago
    service = RepositoryService()
    repository = MagicMock()
    
    state = service.get_repository_state(repository)
    
    assert state == "Inactivo"

@patch('app.services.repository_service.RepositoryService.get_last_commit_date')
def test_get_repository_state_no_commits(mock_get_last_commit_date):
    mock_get_last_commit_date.return_value = None
    service = RepositoryService()
    repository = MagicMock()
    
    state = service.get_repository_state(repository)
    
    assert state == "No hay commits"

@patch('app.services.repository_service.RepositoryService.get_last_commit_date')
def test_get_repository_state_exception(mock_get_last_commit_date):
    mock_get_last_commit_date.side_effect = Exception("Error al obtener commits")
    service = RepositoryService()
    repository = MagicMock()
    
    state = service.get_repository_state(repository)
    
    assert state == "No hay commits"
    mock_get_last_commit_date.assert_called_once()

# Pruebas para count_state_repositories
@patch('app.services.repository_service.RepositoryService.get_repository_state')
def test_count_state_repositories_all_active(mock_get_repository_state):
    mock_get_repository_state.return_value = "Activo"
    service = RepositoryService()
    repos = [MagicMock(), MagicMock(), MagicMock()]
    
    active_count, inactive_count = service.count_state_repositories(repos)
    
    assert active_count == 3
    assert inactive_count == 0

@patch('app.services.repository_service.RepositoryService.get_repository_state')
def test_count_state_repositories_all_inactive(mock_get_repository_state):
    mock_get_repository_state.return_value = "Inactivo"
    service = RepositoryService()
    repos = [MagicMock(), MagicMock(), MagicMock()]
    
    active_count, inactive_count = service.count_state_repositories(repos)
    
    assert active_count == 0
    assert inactive_count == 3

@patch('app.services.repository_service.RepositoryService.get_repository_state')
def test_count_state_repositories_mixed(mock_get_repository_state):
    service = RepositoryService()
    repos = [MagicMock(), MagicMock(), MagicMock()]
    mock_get_repository_state.side_effect = ["Activo", "Inactivo", "Activo"]
    
    active_count, inactive_count = service.count_state_repositories(repos)
    
    assert active_count == 2
    assert inactive_count == 1

@patch('app.services.repository_service.RepositoryService.get_repository_state')
def test_count_state_repositories_empty(mock_get_repository_state):
    service = RepositoryService()
    repos = []
    
    active_count, inactive_count = service.count_state_repositories(repos)
    
    assert active_count == 0
    assert inactive_count == 0

@patch('app.services.repository_service.RepositoryService.get_repository_state')
def test_count_state_repositories_no_commits(mock_get_repository_state):
    mock_get_repository_state.return_value = "No hay commits"
    service = RepositoryService()
    repos = [MagicMock(), MagicMock()]
    
    active_count, inactive_count = service.count_state_repositories(repos)
    
    assert active_count == 0
    assert inactive_count == 0

