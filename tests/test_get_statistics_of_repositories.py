import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from datetime import datetime
from app.services.repository_service import RepositoryService
from app.models.repository_model import RepositoriesStats

@pytest.fixture
def mock_repositories():
    repo1 = MagicMock()
    repo1.name = "repo1"
    repo1.owner.login = "owner1"
    repo1.created_at = datetime(2023, 1, 1)
    repo1.get_issues.return_value = [MagicMock(title="Issue 1"), MagicMock(title="Issue 2")]
    repo1.get_pulls.side_effect = lambda state: (
        [MagicMock(), MagicMock()] if state == "open" else [MagicMock(), MagicMock()]
    ) if state != "all" else [MagicMock(user=MagicMock(login="dependabot")), MagicMock(user=MagicMock(login="dependabot"))]
    repo1.get_collaborators.return_value = [MagicMock(login="collab1"), MagicMock(login="collab2")]
    repo1.get_languages.return_value = {"Python": 1000, "JavaScript": 2000}

    repo2 = MagicMock()
    repo2.name = "repo2"
    repo2.owner.login = "owner2"
    repo2.created_at = datetime(2023, 2, 1)
    repo2.get_issues.return_value = [MagicMock(title="Issue 3")]
    repo2.get_pulls.side_effect = lambda state: (
        [MagicMock()] if state == "open" else [MagicMock(), MagicMock()]
    ) if state != "all" else [MagicMock(user=MagicMock(login="dependabot")), MagicMock(user=MagicMock(login="dependabot"))]
    repo2.get_collaborators.return_value = [MagicMock(login="collab2"), MagicMock(login="collab3")]
    repo2.get_languages.return_value = {"Python": 3000, "TypeScript": 500}

    repos = MagicMock()
    repos.totalCount = 2
    repos.__iter__.return_value = iter([repo1, repo2])
    return repos

@patch('app.services.repository_service.RepositoryService.get_repositories_from_github')
@patch('app.services.repository_service.RepositoryService.count_state_repositories')
def test_get_statistics_of_repositories(mock_count_state_repositories, mock_get_repositories_from_github, mock_repositories):
    mock_get_repositories_from_github.return_value = mock_repositories
    mock_count_state_repositories.return_value = (1, 1)

    service = RepositoryService()
    stats = service.get_statistics_of_repositories()

    assert stats.repositories == 2
    assert stats.repositoriesActives == 1
    assert stats.repositoriesInactives == 1
    assert stats.prsOpen == 3  # 2 from repo1 + 1 from repo2
    assert stats.prsClosed == 4  # 2 from repo1 + 2 from repo2
    assert stats.prsDependabot == 4  # 2 from repo1 + 2 from repo2
    assert stats.collaborators == 3  # 2 from repo1 (collab1, collab2) + 1 from repo2 (collab3, collab2 is duplicate)
    assert stats.issues == 3  # 2 from repo1 + 1 from repo2
    
    # Total bytes: 1000 (Python) + 2000 (JavaScript) + 3000 (Python) + 500 (TypeScript) = 6500
    total_bytes = 6500
    python_percentage = (4000 / total_bytes) * 100  # 4000 bytes of Python
    javascript_percentage = (2000 / total_bytes) * 100  # 2000 bytes of JavaScript
    typescript_percentage = (500 / total_bytes) * 100  # 500 bytes of TypeScript

    assert f"Python: {python_percentage:.2f}%" in stats.percentages_languages
    assert f"JavaScript: {javascript_percentage:.2f}%" in stats.percentages_languages
    assert f"TypeScript: {typescript_percentage:.2f}%" in stats.percentages_languages

@patch('app.services.repository_service.RepositoryService.get_repositories_from_github')
def test_get_statistics_of_repositories_exception(mock_get_repositories_from_github):
    mock_get_repositories_from_github.side_effect = Exception("Error al obtener repositorios")

    service = RepositoryService()

    with pytest.raises(HTTPException) as exc_info:
        service.get_statistics_of_repositories()
    
    assert exc_info.value.status_code == 500
    assert str(exc_info.value.detail) == "Error al obtener estadísticas del repositorio: Error al obtener repositorios"

@patch('app.services.repository_service.RepositoryService.get_repositories_from_github')
def test_get_statistics_of_repositories_collaborators_exception(mock_get_repositories_from_github, mock_repositories, capsys):
    # Mock para simular una excepción al obtener colaboradores
    repo_with_error = MagicMock()
    repo_with_error.name = "repo_with_error"
    repo_with_error.owner.login = "owner_with_error"
    repo_with_error.created_at = datetime(2023, 3, 1)
    repo_with_error.get_issues.return_value = []
    repo_with_error.get_pulls.side_effect = lambda state: []
    repo_with_error.get_collaborators.side_effect = Exception("Error al obtener colaboradores")
    repo_with_error.get_languages.return_value = {}

    # Añadir el repo_with_error al mock_repositories
    mock_repositories.__iter__.return_value = iter([repo_with_error])
    mock_get_repositories_from_github.return_value = mock_repositories

    service = RepositoryService()
    stats = service.get_statistics_of_repositories()


    assert stats.collaborators == 0  
    captured = capsys.readouterr()
    assert "Error al obtener colaboradores" in captured.out  
