import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from faker import Faker
from app.services.repository_service import RepositoryService
from app.models.repository_model import RepositoryStats

fake = Faker()

@pytest.fixture
def mock_repositories():
    repo1 = MagicMock()
    repo1.name = "repo1"
    repo1.get_collaborators.return_value.totalCount = 10
    repo1.get_pulls.side_effect = lambda state: MagicMock(totalCount=4) if state == "open" else MagicMock(totalCount=1)
    repo1.get_issues.return_value.totalCount = 3
    repo1.get_branches.return_value.totalCount = 9
    repo1.get_pulls.return_value = [MagicMock(user=MagicMock(login="dependabot1"))]
    repo1.get_languages.return_value = {"Python": 3000, "JavaScript": 2000}

    repo2 = MagicMock()
    repo2.name = "repo2"
    repo2.get_collaborators.return_value.totalCount = 8
    repo2.get_pulls.side_effect = lambda state: MagicMock(totalCount=6) if state == "open" else MagicMock(totalCount=2)
    repo2.get_issues.return_value.totalCount = 4
    repo2.get_branches.return_value.totalCount = 7
    repo2.get_pulls.return_value = [MagicMock(user=MagicMock(login="dependabot2"))]
    repo2.get_languages.return_value = {"Python": 4000, "TypeScript": 1000}

    repos = [repo1, repo2]
    return repos

@patch('app.services.repository_service.RepositoryService.get_repositories_from_github')
def test_get_statistics_by_detail_success(mock_get_repositories_from_github, mock_repositories):
    mock_get_repositories_from_github.return_value = mock_repositories

    service = RepositoryService()
    stats = service.get_statistics_by_detail("repo1")

    assert stats.collaborators == 10
    assert stats.prsOpen == 4
    assert stats.prsClosed == 1
    assert stats.prsDependabot == 1
    assert stats.issues == 3
    assert stats.branches == 9

    # Verificar los porcentajes de lenguajes
    total_bytes = 3000 + 2000
    python_percentage = (3000 / total_bytes) * 100
    javascript_percentage = (2000 / total_bytes) * 100

    assert f"Python: {python_percentage:.2f}%" in stats.percentagesLanguages
    assert f"JavaScript: {javascript_percentage:.2f}%" in stats.percentagesLanguages

@patch('app.services.repository_service.RepositoryService.get_repositories_from_github')
def test_get_statistics_by_detail_not_found(mock_get_repositories_from_github, mock_repositories):
    mock_get_repositories_from_github.return_value = mock_repositories

    service = RepositoryService()
    with pytest.raises(HTTPException) as exc_info:
        service.get_statistics_by_detail("repo3")

    assert exc_info.value.status_code == 404
    assert str(exc_info.value.detail) == "El repositorio 'repo3' no existe"

@patch('app.services.repository_service.RepositoryService.get_repositories_from_github')
def test_get_statistics_by_detail_exception(mock_get_repositories_from_github):
    mock_get_repositories_from_github.side_effect = Exception("Error al obtener repositorios")

    service = RepositoryService()
    with pytest.raises(HTTPException) as exc_info:
        service.get_statistics_by_detail("repo1")

    assert exc_info.value.status_code == 500
    assert str(exc_info.value.detail) == "Error al obtener estadísticas detalladas del repositorio: Error al obtener repositorios"
