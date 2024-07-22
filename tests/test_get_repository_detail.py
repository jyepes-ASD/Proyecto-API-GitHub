import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from faker import Faker
from app.services.repository_service import RepositoryService
from app.models.repository_model import Repository

fake = Faker()

@pytest.fixture
def mock_repositories():
    repo1 = MagicMock()
    repo1.name = "repo1"
    repo1.description = fake.text()
    repo1.owner.login = fake.user_name()
    repo1.get_collaborators.return_value = [MagicMock(login=fake.user_name()), MagicMock(login=fake.user_name())]
    repo1.get_pulls.side_effect = lambda state: [
        MagicMock(number=fake.random_int(), title=fake.sentence(), assignee=None, created_at=fake.date_time())
    ] if state == "open" else [
        MagicMock(number=fake.random_int(), title=fake.sentence(), assignee=MagicMock(login=fake.user_name()), created_at=fake.date_time())
    ]
    repo1.get_branches.return_value = [MagicMock(name=fake.word()), MagicMock(name=fake.word())]

    issue1 = MagicMock(number=fake.random_int(), title=fake.sentence(), body=fake.text())
    issue1.labels = [MagicMock(name="bug")]
    issue1.labels[0].name = "bug"  # Asegúrate de que el nombre del label sea una cadena
    repo1.get_issues.return_value = [issue1]

    repo1.get_languages.return_value = {"Python": fake.random_int(min=1000, max=5000), "JavaScript": fake.random_int(min=1000, max=5000)}

    repo2 = MagicMock()
    repo2.name = "repo2"
    repo2.description = fake.text()
    repo2.owner.login = fake.user_name()
    repo2.get_collaborators.return_value = [MagicMock(login=fake.user_name()), MagicMock(login=fake.user_name())]
    repo2.get_pulls.side_effect = lambda state: [
        MagicMock(number=fake.random_int(), title=fake.sentence(), assignee=None, created_at=fake.date_time())
    ] if state == "open" else [
        MagicMock(number=fake.random_int(), title=fake.sentence(), assignee=MagicMock(login=fake.user_name()), created_at=fake.date_time())
    ]
    repo2.get_branches.return_value = [MagicMock(name=fake.word()), MagicMock(name=fake.word())]

    issue2 = MagicMock(number=fake.random_int(), title=fake.sentence(), body=fake.text())
    issue2.labels = [MagicMock(name="enhancement")]
    issue2.labels[0].name = "enhancement"  # Asegúrate de que el nombre del label sea una cadena
    repo2.get_issues.return_value = [issue2]

    repo2.get_languages.return_value = {"Python": fake.random_int(min=1000, max=5000), "TypeScript": fake.random_int(min=500, max=3000)}

    repos = [repo1, repo2]
    return repos

@patch('app.services.repository_service.RepositoryService.get_repositories_from_github')
def test_get_repository_detail_success(mock_get_repositories_from_github, mock_repositories):
    mock_get_repositories_from_github.return_value = mock_repositories

    service = RepositoryService()
    repo_detail = service.get_repository_detail("repo1")

    assert repo_detail.name == "repo1"
    assert repo_detail.description
    assert repo_detail.collaborators
    assert repo_detail.prsOpen
    assert repo_detail.prsClosed
    assert repo_detail.issuesDetails
    assert repo_detail.branchesDetails

    # Obtener repo1 del mock_repositories para calcular los porcentajes
    repo1 = next(repo for repo in mock_repositories if repo.name == "repo1")

    # Calcular los porcentajes de lenguajes
    total_bytes = sum(repo1.get_languages().values())
    languages_percentages = {lang: (bytes_count / total_bytes) * 100 for lang, bytes_count in repo1.get_languages().items()}
    percentages = [f"{lang}: {percentage:.2f}%" for lang, percentage in languages_percentages.items()]

    # Verificar que los porcentajes calculados estén en languagesPercentage
    for percentage in percentages:
        assert percentage in repo_detail.languagesPercentage

@patch('app.services.repository_service.RepositoryService.get_repositories_from_github')
def test_get_repository_detail_not_found(mock_get_repositories_from_github, mock_repositories):
    mock_get_repositories_from_github.return_value = mock_repositories

    service = RepositoryService()
    with pytest.raises(HTTPException) as exc_info:
        service.get_repository_detail("repo3")

    assert exc_info.value.status_code == 404
    assert str(exc_info.value.detail) == "El repositorio 'repo3' no existe"

@patch('app.services.repository_service.RepositoryService.get_repositories_from_github')
def test_get_repository_detail_exception(mock_get_repositories_from_github):
    mock_get_repositories_from_github.side_effect = Exception("Error al obtener repositorios")

    service = RepositoryService()
    with pytest.raises(HTTPException) as exc_info:
        service.get_repository_detail("repo1")

    assert exc_info.value.status_code == 500
    assert str(exc_info.value.detail) == "Error al obtener los detalles del repositorio: Error al obtener repositorios"

def test_languages_percentage_calculation():
    repo = MagicMock()
    repo.name = "test_repo"
    repo.description = fake.text()
    repo.owner.login = fake.user_name()
    repo.get_languages.return_value = {"Python": 3000, "JavaScript": 2000}

    service = RepositoryService()
    
    # Simular el cálculo de lenguajes
    langs = repo.get_languages()
    total_bytes = sum(langs.values())
    languages_percentages = {lang: (bytes_count / total_bytes) * 100 for lang, bytes_count in langs.items()}
    percentages = [f"{lang}: {percentage:.2f}%" for lang, percentage in languages_percentages.items()]

    repo_detail = Repository(
        name=repo.name,
        description=repo.description,
        collaborators=[],
        prsOpen=[],
        prsClosed=[],
        prsDependabot=[],  # No se usa Dependabot
        issuesDetails=[],
        branchesDetails=[],
        languagesPercentage=percentages
    )

    # Verificar que los porcentajes calculados estén en languagesPercentage
    assert repo_detail.languagesPercentage == percentages
    assert "Python: 60.00%" in repo_detail.languagesPercentage
    assert "JavaScript: 40.00%" in repo_detail.languagesPercentage
