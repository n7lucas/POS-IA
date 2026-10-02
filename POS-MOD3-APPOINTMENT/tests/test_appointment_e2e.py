# tests/test_appointment_e2e.py
import pytest
from fastapi.testclient import TestClient

from server import create_app
from graph.builder import build_graph
from services.appointment_service import AppointmentService

@pytest.fixture
def app_with_fresh_service():
    """Garante um serviço de agendamentos limpo a cada teste."""
    fresh_service = AppointmentService()
    graph = build_graph(appointment_service=fresh_service)
    app = create_app(compiled_graph=graph)
    return TestClient(app)

def test_schedule_appointment_e2e(app_with_fresh_service):
    """Testa o fluxo completo de agendamento de consulta a partir de texto livre."""
    payload = {
        "message": "Quero agendar uma consulta com a Dra. Ana amanhã às 09:00 para o paciente Erick."
    }
    response = app_with_fresh_service.post("/chat", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "schedule"
    assert data["action_success"] is True
    assert data["action_error"] is None
    assert len(data["output"]) > 0

def test_schedule_conflict_e2e(app_with_fresh_service):
    """Garante que a tentativa de agendar no mesmo horário ocupado falha no serviço."""
    # O mock inicial do AppointmentService já possui um agendamento para o ID 1 no horário '2026-10-10T10:00:00' para o Erick
    payload = {
        "message": "Quero agendar com o Dr. Alicio no dia 10/10/2026 às 10:00 para o paciente Lucas."
    }
    response = app_with_fresh_service.post("/chat", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "schedule"
    assert data["action_success"] is False
    assert "já está ocupado" in data["action_error"]

def test_cancel_appointment_e2e(app_with_fresh_service):
    """Testa o fluxo completo de cancelamento de uma consulta existente."""
    payload = {
        "message": "Quero cancelar minha consulta com o Dr. Alicio no dia 10/10/2026 às 10:00 para o paciente Erick."
    }
    response = app_with_fresh_service.post("/chat", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "cancel"
    assert data["action_success"] is True
    assert data["action_error"] is None

def test_fallback_unclear_intent_e2e(app_with_fresh_service):
    """Garante que frases sem intenção clara caem no nó de fallback."""
    payload = {
        "message": "Qual é a previsão do tempo para amanhã?"
    }
    response = app_with_fresh_service.post("/chat", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "unknown"
    assert data["action_success"] is False