# Visão Geral dos Arquivos do Módulo 4
.
├── config.py                     # Pydantic Settings (Limites de tokens, URIs, Chaves)
├── models.py                     # Schemas do Chat, Preferências e Resumo
├── prompts.py                    # Templates do Chat e da Sumarização Incremental
├── main.py                       # CLI para conversa interativa no terminal
├── graph/
│   ├── state.py                  # GraphState com add_messages e flags
│   ├── nodes.py                  # chat_node, save_preferences_node, summarize_node
│   └── builder.py                # Factory do Grafo compilado com Postgres Checkpointer
├── services/
│   ├── openrouter_service.py     # Cliente LLM com Structured Output e Fallback
│   ├── preferences_service.py    # Persistência leve no SQLite (aiosqlite)
│   └── memory_service.py         # Checkpointer de rastreabilidade no Postgres
└── tests/
    └── test_memory_e2e.py        # Suíte E2E de testes de memória e fusão de estado

    # 🎵 Song Highlights Recommender — Agent com Memória Dual & Compactação de Contexto

Um agente de recomendação musical personalizado construído com **LangGraph**, **Python (asyncio)**, **Pydantic V2** e **OpenRouter (com fallback para OpenAI)**.

O projeto implementa uma arquitetura de **Memória Dual** para resolver o problema clássico de crescimento desenfreado da janela de contexto em aplicações LLM: mantém a rastreabilidade completa das conversas e compacta o histórico incrementalmente para otimizar o custo de tokens sem perder o contexto do usuário.

---

## 📸 Arquitetura de Memória Dual

```text
===================================================================================
                       DUAL STORAGE MEMORY ARCHITECTURE                            
===================================================================================

                        +----------------------------+
                        |      LangGraph State       |
                        +--------------+-------------+
                                       |
                +----------------------+----------------------+
                |                                             |
                v                                             v
  [ Long-Term Preferences & Summary ]          [ Raw Execution & State Checkpoints ]
  +---------------------------------+          +-----------------------------------+
  | PreferencesService (SQLite)     |          | MemoryService (Postgres)          |
  +---------------------------------+          +-----------------------------------+
  | • user_preferences              |          | • checkpoints                     |
  | • conversation_summaries        |          | • checkpoint_writes               |
  | • Fast key-value retrieval      |          | • Full trace & thread durability  |
  +---------------------------------+          +-----------------------------------+

```

### Componentes de Armazenamento:

1. **Curto Prazo (PostgreSQL + Checkpointer):**
* Persiste checkpoints e histórico de execução do LangGraph via `AsyncPostgresSaver` e `psycopg_pool`.
* Permite retomar threads de conversa a qualquer momento de forma assíncrona.


2. **Longo Prazo (SQLite + `aiosqlite`):**
* Armazena preferências estruturadas do usuário (nome, idade, gêneros favoritos, artistas/bandas e informações de contexto) extraídas via *Structured Output*.
* Mantém o **Resumo Incremental da Conversa** para injetar contexto enxuto nas mensagens.


3. **Compactador de Contexto (`summarize_node`):**
* Quando o número de mensagens ativas atinge o limite configurado (`MAX_MESSAGES_TO_SUMMARY`), o nó gera um resumo incremental, persiste no SQLite e remove as mensagens antigas da memória ativa usando `RemoveMessage`.



---

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3.12+ (Asyncio)
* **Gerenciador de Pacotes:** `uv`
* **Orquestração de Agentes:** LangGraph (`langgraph`, `langgraph-checkpoint-postgres`)
* **Provedor de LLM:** OpenRouter (`google/gemini-2.0-flash-lite-preview-02-05:free`) com Fallback automático para a API oficial da OpenAI (`gpt-4o-mini`)
* **Validação de Dados:** Pydantic V2 & `pydantic-settings`
* **Bancos de Dados:** PostgreSQL 16 (Docker) & SQLite (`aiosqlite`)
* **Observabilidade:** LangSmith Tracing V2
* **Testes:** Pytest & Pytest-Asyncio

---

## 📂 Estrutura do Projeto

```text
.
├── config.py                     # Configurações globais e leitura do .env (Pydantic Settings)
├── models.py                     # Pydantic Schemas (UserPreferences, ChatResponseSchema, SummarySchema)
├── prompts.py                    # Prompts centralizados para extração e sumarização
├── main.py                       # CLI Interativo para terminal
├── langgraph.json                # Manifesto de configuração para LangGraph Studio / CLI
├── docker-compose.yml            # Infraestrutura local do PostgreSQL
├── graph/
│   ├── state.py                  # Definição do GraphState (add_messages)
│   ├── nodes.py                  # Nós do grafo (chat, save_preferences, summarize)
│   └── builder.py                # Factory do Grafo (compatível com LangGraph Studio & Pytest)
├── services/
│   ├── openrouter_service.py     # Cliente LLM com Structured Output e Provider Fallback
│   ├── preferences_service.py    # Gerenciador SQLite para preferências e resumos
│   └── memory_service.py         # Gerenciador da pool do Postgres com suporte a Windows Asyncio
└── tests/
    └── test_memory_e2e.py        # Suíte de testes automatizados E2E

```

---

## 🚀 Como Executar o Projeto

### Pró-requisitos

* **Python 3.12+** e o gerenciador **`uv`** instalados.
* **Docker Desktop** rodando na sua máquina.

### 1. Configurar Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto contendo suas chaves:

```env
# Provedores LLM
OPENROUTER_API_KEY=sk-or-v1-sua-chave-openrouter
OPENAI_API_KEY=sk-proj-sua-chave-openai-fallback

# Bancos de Dados
POSTGRES_URI=postgresql://postgres:postgres@localhost:5432/song_highlights
SQLITE_DB_PATH=preferences.db

# Limite de Mensagens para Gatilho de Sumarização
MAX_MESSAGES_TO_SUMMARY=4

# LangSmith Observability
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=lsv2_pt_sua_chave_langsmith
LANGCHAIN_PROJECT=song-highlights-recommender

```

### 2. Subir o Banco de Dados PostgreSQL (Docker)

```powershell
docker compose up -d

```

### 3. Executar o Agent no Terminal (CLI)

```powershell
$env:PYTHONPATH="."
uv run python main.py

```

### 4. Executar via LangGraph Studio / CLI

Para testar o agente visualmente no LangGraph Studio:

```powershell
uv run langgraph dev

```

---

## 🧪 Executando os Testes Automatizados

A suíte de testes valida a mescla de preferências no SQLite, o salvamento assíncrono e o disparo do nó de sumarização.

```powershell
$env:PYTHONPATH="."
uv run pytest -v

```


Com certeza! Abaixo está o **diagrama completo do fluxo de execução do grafo**, detalhando a dinâmica dos nós, tomadas de decisão condicionais e a interação com os dois bancos de dados (**PostgreSQL** e **SQLite**):

```text
                                                                    ===================================================================================================
                                                                                                LANGGRAPH DUAL-MEMORY EXECUTION FLOW                                  
                                                                    ===================================================================================================

                                                                                                    [ Mensagem do Usuário ]
                                                                                                                |
                                                                                                                v
                                                                                                            +---------+
                                                                                                            | [START] |
                                                                                                            +----+----+
                                                                                                                |
                                                                                                                v
                                                                                                +-----------------------------------+
                                                                                                |             chat_node             |
                                                                                                +-----------------+-----------------+
                                                                                                                |
                                                                        • Lê preferências e resumo do SQLite (get_preferences / get_summary)
                                                                        • Executa chamada à LLM com Output Estruturado (ChatResponseSchema)
                                                                        • Define flags no State: should_save_preferences & need_summarization
                                                                                                                |
                                                                        +--------------------------------------+--------------------------------------+
                                                                        |                                      |                                      |
                                                                    (should_save_preferences = True)     (need_summarization = True)            (Nenhuma flag ativada)
                                                                        |                                      |                                      |
                                                                        v                                      |                                      v
                                                                    +-----------------------+                     |                                  +-------+
                                                                    | save_preferences_node |                     |                                  | [END] |
                                                                    +-----------+-----------+                     |                                  +-------+
                                                                                |                                 |
                                                                                • Mescla incrementalmente         |
                                                                                dados no SQLite                 |
                                                                                • Limpa extracted_preferences     |
                                                                                |                                 |
                                                                                +-----------------+---------------+
                                                                                                |
                                                                                        (need_summarization = True)
                                                                                                |
                                                                                                v
                                                                                    +--------------------+
                                                                                    |   summarize_node   |
                                                                                    +---------+----------+
                                                                                                |
                                                                                    • Gera resumo incremental do histórico ativo
                                                                                    • Salva o novo resumo no SQLite
                                                                                    • Dispara RemoveMessage para limpar mensagens antigas da memória RAM
                                                                                                |
                                                                                                v
                                                                                            +-----+
                                                                                            | [END]|
                                                                                            +-----+

                                                                    ===================================================================================================
                                                                                                    PERSISTENCE LAYER ARCHITECTURE                                  
                                                                    ===================================================================================================

                                                                    +-----------------------------------+               +-----------------------------------+
                                                                    |    PostgreSQL (Checkpointer)      |               |         SQLite (aiosqlite)        |
                                                                    +-----------------------------------+               +-----------------------------------+
                                                                    | • Histórico bruto de mensagens    |               | • user_preferences                |
                                                                    | • Estado e checkpoints do grafo   |               |   (Nome, Idade, Gêneros, Artistas) |
                                                                    | • Rastreabilidade por thread_id   |               | • conversation_summaries          |
                                                                    | • Resiliência e longa duração     |               |   (Resumo compacto por user_id)   |
                                                                    +-----------------------------------+               +-----------------------------------+

                                                                    ```

---

### Destaques do Fluxo:

1. **Atalhos Eficientes:** Se a interação for uma mensagem comum (sem novas preferências nem limite de histórico estourado), o grafo encerra direto no `[END]` após o `chat_node`.
2. **Execução Encadeada de Nós:** Se o usuário revelar dados pessoais e atingir o limite de mensagens no mesmo turno, o grafo navega do `chat_node` $\rightarrow$ `save_preferences_node` $\rightarrow$ `summarize_node` $\rightarrow$ `[END]`.
3. **Compactação via `RemoveMessage`:** O `summarize_node` remove as mensagens antigas do histórico do LangGraph, garantindo que o `chat_node` só reenvie as últimas duas mensagens acompanhadas do resumo leve do SQLite nas próximas chamadas!