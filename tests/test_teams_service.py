import pytest
from unittest import mock
from fastapi import HTTPException
from app.routers.teams_router import TeamsService
from app.models.teams_model import Team, Member, TeamsResponse
from faker import Faker

fake = Faker()

# Crear un fixture para el servicio de equipos
@pytest.fixture
def teams_service():
    return TeamsService()

def test_get_teams_success(teams_service):
    # Mockear el cliente de GitHub
    with mock.patch.object(teams_service.github_client, 'get_organization') as mock_get_organization:
        # Crear datos falsos para los equipos y miembros
        fake_teams = []
        for _ in range(3):
            team_id = fake.random_int()
            team_name = fake.word()
            members = []
            for _ in range(2):
                member_id = fake.random_int()
                member_login = fake.user_name()
                member_mock = mock.Mock(id=member_id, login=member_login)
                members.append(member_mock)

            team_mock = mock.Mock()
            team_mock.id = team_id
            team_mock.name = team_name
            team_mock.get_members.return_value = members
            fake_teams.append(team_mock)

        mock_org = mock.Mock()
        mock_org.get_teams.return_value = fake_teams
        mock_get_organization.return_value = mock_org

        # Llamar al método get_teams y verificar los resultados
        response = teams_service.get_teams()
        assert isinstance(response, TeamsResponse)
        assert response.total_teams == 3
        assert len(response.teams) == 3
        for team in response.teams:
            assert isinstance(team, Team)
            assert len(team.members) == 2
            for member in team.members:
                assert isinstance(member, Member)

def test_get_teams_failure(teams_service):
    # Mockear una excepción al obtener la organización de GitHub
    with mock.patch.object(teams_service.github_client, 'get_organization', side_effect=Exception('Error de GitHub')):
        with pytest.raises(HTTPException) as excinfo:
            teams_service.get_teams()
        assert excinfo.value.status_code == 500
        assert 'Error al obtener los equipos: Error de GitHub' in excinfo.value.detail
