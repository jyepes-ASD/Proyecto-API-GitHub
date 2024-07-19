from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_teams_success():
    mock_org = MagicMock()
    mock_team = MagicMock()
    mock_team.id = 1
    mock_team.name = "Test Team"
    mock_member = MagicMock()
    mock_member.id = 1
    mock_member.login = "test_member"
    mock_team.get_members.return_value = [mock_member]
    mock_org.get_teams.return_value = [mock_team]
    
    with patch('routers.teams_router.my_git.get_organization', return_value=mock_org):
        response = client.get("/orgs/test_org/teams")
        assert response.status_code == 200
        data = response.json()
        
        assert len(data['teams']) == 1
        assert data['teams'][0]['id'] == 1
        assert data['teams'][0]['name'] == "Test Team"
        assert data['teams'][0]['members_count'] == 1  # Aquí se usa members_count en lugar de membersCount
        assert data['teams'][0]['members'][0]['id'] == 1
        assert data['teams'][0]['members'][0]['login'] == "test_member"

def test_get_teams_org_not_found():
    with patch('routers.teams_router.my_git.get_organization', side_effect=Exception("Organization not found")):
        response = client.get("/orgs/unknown_org/teams")
        assert response.status_code == 500
        assert response.json() == {"detail": "Error al obtener los equipos: Organization not found"}

def test_get_teams_exception():
    with patch('routers.teams_router.my_git.get_organization', side_effect=Exception("Error al conectar con GitHub")):
        response = client.get("/orgs/test_org/teams")
        assert response.status_code == 500
        assert response.json() == {"detail": "Error al obtener los equipos: Error al conectar con GitHub"}
