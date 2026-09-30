# tests/test_router_e2e.py
import pytest
from fastapi.testclient import TestClient
from config import OpenRouterConfig
from services.openrouter_service import OpenRouterService
from server import create_app

@pytest.fixture
def client_price_strategy():
    """Cria um cliente de teste configurado com estratégia de Menor Preço."""
    custom_config = OpenRouterConfig(provider_sort_by="price")
    custom_service = OpenRouterService(config_override=custom_config)
    app = create_app(service=custom_service)
    return TestClient(app)

@pytest.fixture
def client_throughput_strategy():
    """Cria um cliente de teste configurado com estratégia de Maior Throughput."""
    custom_config = OpenRouterConfig(provider_sort_by="throughput")
    custom_service = OpenRouterService(config_override=custom_config)
    app = create_app(service=custom_service)
    return TestClient(app)

def test_router_default_price_strategy(client_price_strategy):
    """Garante que a rota responde com sucesso sob a estratégia de preço."""
    response = client_price_strategy.post(
        "/chat", 
        json={"question": "Explique o que é orientação a objetos em uma frase."}
    )
    assert response.status_code == 200
    data = response.json()
    assert "model" in data
    assert "content" in data
    assert len(data["content"]) > 0

def test_router_throughput_strategy(client_throughput_strategy):
    """Garante que a rota responde com sucesso sob a estratégia de velocidade/throughput."""
    response = client_throughput_strategy.post(
        "/chat", 
        json={"question": "Explique o que é orientação a objetos em uma frase."}
    )
    assert response.status_code == 200
    data = response.json()
    assert "model" in data
    assert "content" in data