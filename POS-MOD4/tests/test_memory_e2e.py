# tests/test_memory_e2e.py
import pytest
import os
from langchain_core.messages import HumanMessage
from graph.builder import create_graph
from services.preferences_service import PreferencesService
from services.memory_service import MemoryService
from models import UserPreferences

TEST_SQLITE_DB = "test_preferences.db"


@pytest.fixture
async def setup_test_services():
    """Fixture que cria serviços e banco de testes limpos."""
    pref_service = PreferencesService(TEST_SQLITE_DB)
    mem_service = MemoryService()
    await pref_service.init_db()

    yield pref_service, mem_service

    # Teardown: Limpa banco de testes
    await mem_service.close()
    if os.path.exists(TEST_SQLITE_DB):
        os.remove(TEST_SQLITE_DB)


@pytest.mark.asyncio
async def test_merge_preferences_sqlite(setup_test_services):
    """Valida o merge incremental no SQLite sem sobrescrever dados anteriores."""
    pref_service, _ = setup_test_services
    user_id = "test_user_1"

    # 1. Primeira gravação
    pref1 = UserPreferences(name="Lucas", age=25, favorite_genres=["Rock"])
    await pref_service.merge_preferences(user_id, pref1)

    # 2. Segunda gravação incremental
    pref2 = UserPreferences(favorite_genres=["Metal"], favorite_artists=["Iron Maiden"])
    updated = await pref_service.merge_preferences(user_id, pref2)

    # Asserções
    assert updated.name == "Lucas"
    assert updated.age == 25
    assert "Rock" in updated.favorite_genres
    assert "Metal" in updated.favorite_genres
    assert "Iron Maiden" in updated.favorite_artists


@pytest.mark.asyncio
async def test_full_memory_flow_e2e(setup_test_services):
    """Testa a execução do grafo, salvamento de preferências e gatilho do resumo."""
    pref_service, mem_service = setup_test_services
    graph = await create_graph(preferences_service=pref_service, memory_service=mem_service)

    user_id = "test_user_e2e"
    config = {"configurable": {"thread_id": "thread_test_1", "user_id": user_id}}

    # Interação 1: Apresentação e preferências
    msg1 = {"messages": [HumanMessage(content="Oi, meu nome é Lucas, tenho 28 anos e amo Heavy Metal.")], "user_id": user_id}
    res1 = await graph.ainvoke(msg1, config=config)

    assert res1.get("user_context") is not None
    assert res1["user_context"].name == "Lucas"

    # Interação 2: Segunda mensagem para forçar o limite de sumarização
    msg2 = {"messages": [HumanMessage(content="Recomende 3 bandas clássicas para eu ouvir hoje à noite.")], "user_id": user_id}
    res2 = await graph.ainvoke(msg2, config=config)

    # Garante que o resumo foi gerado e mantido no SQLite
    summary = await pref_service.get_summary(user_id)
    assert summary is not None