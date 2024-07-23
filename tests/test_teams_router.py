import unittest
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient
from fastapi import HTTPException
from app.main import app
from app.models.teams_model import TeamsResponse

client = TestClient(app)

class TestTeamsRouter(unittest.TestCase):


    @patch('app.services.teams_service.teams_service.get_teams')
    def test_get_teams_http_exception(self, mock_get_teams):
        # Configurar el mock para que lance una HTTPException
        mock_get_teams.side_effect = HTTPException(status_code=404, detail="Teams not found")

        # Hacer la solicitud a la ruta
        response = client.get("/orgs/teams")

        # Verificar que la respuesta sea un error 404
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Teams not found"})

    @patch('app.services.teams_service.teams_service.get_teams')
    def test_get_teams_general_exception(self, mock_get_teams):
        # Configurar el mock para que lance una excepción general
        mock_get_teams.side_effect = Exception("Unexpected error")

        # Hacer la solicitud a la ruta
        response = client.get("/orgs/teams")

        # Verificar que la respuesta sea un error 500
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json(), {"detail": "Error al obtener los equipos: Unexpected error"})

if __name__ == '__main__':
    unittest.main()