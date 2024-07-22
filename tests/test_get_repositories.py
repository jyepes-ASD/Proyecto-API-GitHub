import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from datetime import datetime
from app.services.repository_service import RepositoryService
from app.models.repository_model import Repositories

@pytest.fixture
def mock_github_user():
    user = MagicMock()
    repo1 = MagicMock()
    repo1.name = "repo1"
    repo1.owner.login = "owner1"
    repo1.created_at = datetime(2023, 1, 1)
    repo1.description = "Repository 1 description"
    
    repo2 = MagicMock()
    repo2.name = "repo2"
    repo2.owner.login = "owner2"
    repo2.created_at = datetime(2023, 2, 1)
    repo2.description = "Repository 2 description"
    
    user.get_repos.return_value = [repo1, repo2]
    return user

@patch('app.services.repository_service.RepositoryService.get_repositories_from_github')
@patch('app.services.repository_service.RepositoryService.get_last_commit_date')
@patch('app.services.repository_service.RepositoryService.get_repository_state')
def test_get_repositories_success(mock_get_repository_state, mock_get_last_commit_date, mock_get_repositories_from_github, mock_github_user):
    mock_get_repositories_from_github.return_value = mock_github_user.get_repos()
    mock_get_last_commit_date.side_effect = [datetime(2023, 1, 1), datetime(2023, 2, 1)]
    mock_get_repository_state.side_effect = ["Activo", "Inactivo"]

    service = RepositoryService()
    repositories = service.get_repositories()

    assert len(repositories) == 2

    assert repositories[0].owner == "owner1"
    assert repositories[0].name == "repo1"
    assert repositories[0].createDate == datetime(2023, 1, 1)
    assert repositories[0].lastUseDate == datetime(2023, 1, 1)
    assert repositories[0].state == "Activo"
    
    assert repositories[1].owner == "owner2"
    assert repositories[1].name == "repo2"
    assert repositories[1].createDate == datetime(2023, 2, 1)
    assert repositories[1].lastUseDate == datetime(2023, 2, 1)
    assert repositories[1].state == "Inactivo"

@patch('app.services.repository_service.RepositoryService.get_repositories_from_github')
def test_get_repositories_exception(mock_get_repositories_from_github):
    mock_get_repositories_from_github.side_effect = Exception("Error al obtener los repositorios")
    
    service = RepositoryService()
    
    with pytest.raises(HTTPException) as exc_info:
        service.get_repositories()
    
    assert exc_info.value.status_code == 500
    assert str(exc_info.value.detail) == "Error al obtener los repositorios: Error al obtener los repositorios"
