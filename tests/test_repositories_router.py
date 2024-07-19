# tests/test_repositories_router.py

from fastapi import FastAPI, HTTPException
import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from routers.repositories_router import (
    get_repositories_from_github,
    get_last_commit_date,
    get_repository_state,
    count_state_repositories,
    repository_router,
    get_repositories,
    get_statistics_of_repositories,
    get_repository_detail
)
from faker import Faker
from token_1 import my_git
from datetime import datetime, timedelta
from models.repository_model import Repositories, RepositoriesStats, Repository

fake = Faker()

# Crear cliente de prueba
app = FastAPI()
app.include_router(repository_router)
client = TestClient(app)

# Mock del usuario de GitHub
@pytest.fixture
def mock_github_user():
    mock_user = Mock()
    mock_repo = Mock()
    mock_repo.name = fake.word()
    mock_user.get_repos.return_value = [mock_repo]
    return mock_user

# Pruebas para get_repositories_from_github

# Prueba de éxito
def test_get_repositories_from_github_success(mock_github_user):
    with patch('routers.repositories_router.my_git.get_user', return_value=mock_github_user):
        repos = get_repositories_from_github()
        assert len(repos) > 0
        assert repos[0].name == mock_github_user.get_repos()[0].name

# Prueba de excepción
def test_get_repositories_from_github_exception():
    with patch('routers.repositories_router.my_git.get_user', side_effect=Exception("Error de conexión")):
        with pytest.raises(HTTPException) as exc_info:
            get_repositories_from_github()
        assert exc_info.value.status_code == 500
        assert "Error al obtener los repositorios" in str(exc_info.value.detail)

# Pruebas para get_last_commit_date

# Prueba de éxito
def test_get_last_commit_date_success():
    mock_commit = Mock()
    mock_commit.commit.committer.date = fake.date_time_this_year()

    mock_repo = Mock()
    mock_repo.get_commits.return_value = [mock_commit]

    commit_date = get_last_commit_date(mock_repo)
    assert commit_date == mock_commit.commit.committer.date

# Prueba sin commits
def test_get_last_commit_date_no_commits():
    mock_repo = Mock()
    mock_repo.get_commits.return_value = []

    commit_date = get_last_commit_date(mock_repo)
    assert commit_date is None

# Prueba de excepción
def test_get_last_commit_date_exception():
    mock_repo = Mock()
    mock_repo.get_commits.side_effect = Exception("Error al obtener commits")

    commit_date = get_last_commit_date(mock_repo)
    assert commit_date is None

# Pruebas para get_repository_state

# Prueba con estado Activo
def test_get_repository_state_active():
    mock_repo = Mock()
    recent_date = datetime.now() - timedelta(days=30)
    with patch('routers.repositories_router.get_last_commit_date', return_value=recent_date):
        state = get_repository_state(mock_repo)
        assert state == "Activo"

# Prueba con estado Inactivo
def test_get_repository_state_inactive():
    mock_repo = Mock()
    old_date = datetime.now() - timedelta(days=180)
    with patch('routers.repositories_router.get_last_commit_date', return_value=old_date):
        state = get_repository_state(mock_repo)
        assert state == "Inactivo"

# Prueba sin commits
def test_get_repository_state_no_commits():
    mock_repo = Mock()
    with patch('routers.repositories_router.get_last_commit_date', return_value=None):
        state = get_repository_state(mock_repo)
        assert state == "No hay commits"

# Prueba de excepción
def test_get_repository_state_exception():
    mock_repo = Mock()
    with patch('routers.repositories_router.get_last_commit_date', side_effect=Exception("Error al obtener commits")):
        state = get_repository_state(mock_repo)
        assert state == "No hay commits"

# Pruebas para count_state_repositories

# Prueba con repositorios activos e inactivos
def test_count_state_repositories_mixed():
    active_repo = Mock()
    inactive_repo = Mock()
    with patch('routers.repositories_router.get_repository_state', side_effect=["Activo", "Inactivo"]):
        active_count, inactive_count = count_state_repositories([active_repo, inactive_repo])
        assert active_count == 1
        assert inactive_count == 1

# Prueba con todos los repositorios activos
def test_count_state_repositories_all_active():
    repos = [Mock() for _ in range(5)]
    with patch('routers.repositories_router.get_repository_state', return_value="Activo"):
        active_count, inactive_count = count_state_repositories(repos)
        assert active_count == 5
        assert inactive_count == 0

# Prueba con todos los repositorios inactivos
def test_count_state_repositories_all_inactive():
    repos = [Mock() for _ in range(5)]
    with patch('routers.repositories_router.get_repository_state', return_value="Inactivo"):
        active_count, inactive_count = count_state_repositories(repos)
        assert active_count == 0
        assert inactive_count == 5

# Pruebas para el endpoint get_repositories

# Prueba de éxito para el endpoint get_repositories
def test_get_repositories_endpoint_success(mock_github_user):
    mock_repo = Mock()
    mock_repo.owner.login = fake.user_name()
    mock_repo.name = fake.word()
    mock_repo.created_at = fake.date_time_this_year()
    mock_repo.get_commits.return_value = [Mock(commit=Mock(committer=Mock(date=fake.date_time_this_year())))]
    mock_repos = [mock_repo]

    with patch('routers.repositories_router.get_repositories_from_github', return_value=mock_repos):
        with patch('routers.repositories_router.get_last_commit_date', return_value=fake.date_time_this_year()):
            with patch('routers.repositories_router.get_repository_state', return_value="Activo"):
                response = client.get("/repositories")
                assert response.status_code == 200
                assert len(response.json()) == 1
                assert response.json()[0]['name'] == mock_repo.name

# Prueba de excepción para el endpoint get_repositories
def test_get_repositories_endpoint_exception():
    with patch('routers.repositories_router.get_repositories_from_github', side_effect=Exception("Error al obtener los repositorios")):
        response = client.get("/repositories")
        assert response.status_code == 500
        assert response.json()['detail'].startswith("Error al obtener los repositorios")

# Pruebas para el endpoint get_statistics_of_repositories

# Prueba de éxito para el endpoint get_statistics_of_repositories
def test_get_statistics_of_repositories_success():
    mock_repo1 = MagicMock()
    mock_repo1.owner.login = fake.user_name()
    mock_repo1.name = fake.word()
    mock_repo1.created_at = fake.date_time_this_year()
    mock_repo1.get_issues.return_value = [MagicMock(title=fake.sentence())]
    mock_repo1.get_pulls.side_effect = lambda state: [MagicMock()] * (5 if state == "open" else 3)
    mock_repo1.get_collaborators.return_value = [MagicMock(login=fake.user_name()) for _ in range(2)]
    mock_repo1.get_languages.return_value = {'Python': 12345, 'JavaScript': 6789}

    mock_repo2 = MagicMock()
    mock_repo2.owner.login = fake.user_name()
    mock_repo2.name = fake.word()
    mock_repo2.created_at = fake.date_time_this_year()
    mock_repo2.get_issues.return_value = [MagicMock(title=fake.sentence())]
    mock_repo2.get_pulls.side_effect = lambda state: [MagicMock()] * (5 if state == "open" else 3)
    mock_repo2.get_collaborators.return_value = [MagicMock(login=fake.user_name()) for _ in range(2)]
    mock_repo2.get_languages.return_value = {'Python': 11111, 'JavaScript': 2222}

    dependabot_pr = MagicMock()
    dependabot_pr.user.login = 'dependabot'
    mock_repo1.get_pulls.side_effect = lambda state: [dependabot_pr] * 3 if state == 'all' else [MagicMock()] * (5 if state == "open" else 3)
    mock_repo2.get_pulls.side_effect = lambda state: [dependabot_pr] * 3 if state == 'all' else [MagicMock()] * (5 if state == "open" else 3)

    mock_repos = MagicMock()
    mock_repos.totalCount = 2
    mock_repos.__iter__.return_value = iter([mock_repo1, mock_repo2])

    with patch('routers.repositories_router.get_repositories_from_github', return_value=mock_repos):
        with patch('routers.repositories_router.count_state_repositories', return_value=(1, 1)):
            response = client.get("/repositories/statistics/")
            if response.status_code != 200:
                print(response.json())  # Depuración adicional
            assert response.status_code == 200
            data = response.json()
            
            assert data['repositories'] == 2
            assert data['repositoriesActives'] == 1
            assert data['repositoriesInactives'] == 1
            assert data['prsOpen'] == 10
            assert data['prsClosed'] == 6
            assert data['prsDependabot'] == 6
            assert data['collaborators'] == 4
            assert data['issues'] == 2

            # Verificación ajustada para los porcentajes de lenguajes
            python_percentage = (12345 + 11111) / (12345 + 6789 + 11111 + 2222) * 100
            javascript_percentage = (6789 + 2222) / (12345 + 6789 + 11111 + 2222) * 100
            assert f"Python: {python_percentage:.2f}%" in data['percentages_languages']
            assert f"JavaScript: {javascript_percentage:.2f}%" in data['percentages_languages']

# Prueba de excepción para el endpoint get_statistics_of_repositories
def test_get_statistics_of_repositories_exception():
    with patch('routers.repositories_router.get_repositories_from_github', side_effect=Exception("Error al obtener estadísticas del repositorio")):
        response = client.get("/repositories/statistics/")
        assert response.status_code == 500
        assert response.json()['detail'].startswith("Error al obtener estadísticas del repositorio")

# Pruebas para el endpoint get_repository_detail

# Prueba de éxito para el endpoint get_repository_detail
def test_get_repository_detail_success():
    mock_repo = MagicMock()
    mock_repo.owner.login = fake.user_name()
    mock_repo.name = "test_repo"
    mock_repo.description = fake.sentence()
    mock_repo.get_collaborators.return_value = [MagicMock(login=fake.user_name()) for _ in range(2)]
    mock_repo.get_pulls.side_effect = lambda state: [MagicMock(number=i, title=fake.sentence(), assignee=None, created_at=fake.date_time_this_year()) for i in range(1, 6)] if state == "open" else [MagicMock(number=i, title=fake.sentence(), assignee=None, created_at=fake.date_time_this_year()) for i in range(1, 4)]
    mock_repo.get_branches.return_value = [MagicMock(name=f"branch_{i}") for i in range(1, 4)]
    mock_repo.get_issues.return_value = [MagicMock(number=i, title=fake.sentence(), body=fake.text(), labels=[MagicMock(name=f"label_{j}") for j in range(1, 3)]) for i in range(1, 4)]
    mock_repo.get_languages.return_value = {'Python': 12345, 'JavaScript': 6789}

    mock_repos = MagicMock()
    mock_repos.__iter__.return_value = iter([mock_repo])

    with patch('routers.repositories_router.get_repositories_from_github', return_value=mock_repos):
        response = client.get("/repositories/test_repo/detail")
        if response.status_code != 200:
            print(response.json())  # Depuración adicional
        assert response.status_code == 200
        data = response.json()

        assert data['name'] == "test_repo"
        assert 'description' in data
        assert len(data['collaborators']) == 2
        assert len(data['prsOpen']) == 5
        assert len(data['prsClosed']) == 3
        assert len(data['branchesDetails']) == 3
        assert len(data['issuesDetails']) == 3

        # Verificación ajustada para los porcentajes de lenguajes
        python_percentage = 12345 / (12345 + 6789) * 100
        javascript_percentage = 6789 / (12345 + 6789) * 100
        assert f"Python: {python_percentage:.2f}%" in data['languagesPercentage']
        assert f"JavaScript: {javascript_percentage:.2f}%" in data['languagesPercentage']

# Prueba de repositorio no encontrado para el endpoint get_repository_detail
def test_get_repository_detail_not_found():
    mock_repo = MagicMock()
    mock_repo.name = "another_repo"

    mock_repos = MagicMock()
    mock_repos.__iter__.return_value = iter([mock_repo])

    with patch('routers.repositories_router.get_repositories_from_github', return_value=mock_repos):
        response = client.get("/repositories/unknown_repo/detail")
        assert response.status_code == 404
        assert response.json() == {"detail": "El repositorio 'unknown_repo' no existe"}

# Prueba de excepción para el endpoint get_repository_detail
def test_get_repository_detail_exception():
    with patch('routers.repositories_router.get_repositories_from_github', side_effect=Exception("Error al obtener detalles del repositorio")):
        response = client.get("/repositories/test_repo/detail")
        assert response.status_code == 500
        assert response.json() == {"detail": "Error al obtener los detalles del repositorio: Error al obtener detalles del repositorio"}
