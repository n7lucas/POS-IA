# Instructions to run de Code

Para rodar o código de forma simples e profissional em Python, o fluxo é bem direto. Como você mencionou que usa o uv, vamos utilizar o uv para gerenciar as dependências e o ambiente virtual, mas também deixo o modo tradicional com pip e venv.

## Passo 1: Configurar as Variáveis de Ambiente
Na raiz do seu projeto, crie o arquivo .env com a sua chave do OpenRouter:

Snippet de código
```python
    OPENROUTER_API_KEY=sk-or-v1-sua-chave-aqui
    PORT=3000
```


## Passo 2: Instalar as Dependências
Opção A: Utilizando uv (Recomendado)
Se você já usa o uv, pode sincronizar e instalar as dependências necessárias diretamente no ambiente local com um único comando:

Bash
uv pip install fastapi uvicorn openai pydantic-settings pytest httpx
Opção B: Utilizando Python padrão (venv + pip)
Se preferir o fluxo tradicional do Python:

Crie e ative o ambiente virtual:

Linux/macOS:

Bash
python -m venv .venv
source .venv/bin/activate
Windows (PowerShell):

PowerShell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
Instale as dependências:

Bash
pip install fastapi uvicorn openai pydantic-settings pytest httpx

## Passo 3: Executar o Servidor FastAPI
Para subir o servidor HTTP da API no ar, execute o arquivo main.py:

Com uv:
Bash
uv run python main.py
Sem uv (com a venv ativa):
Bash
python main.py
Você verá a saída no terminal indicando que o servidor Uvicorn está rodando:

Plaintext
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:3000 (Press CTRL+C to quit)

## Passo 4: Testar a API Manualmente
Com o servidor rodando, você pode testar o endpoint /chat de duas formas:

Via Swagger UI (Nativo do FastAPI):
Acesse no navegador: http://localhost:3000/docs
Lá você encontrará a interface gráfica interativa para enviar requisições POST /chat diretamente.

Via curl (no Terminal ou PowerShell):

Bash
curl -X POST "http://localhost:3000/chat" \
     -H "Content-Type: application/json" \
     -d '{"question": "Explique o que e orientacao a objetos em uma frase."}'

# EXECUTAR TESTES

## Passo 5: Executar os Testes Automatizados com Pytest
Para rodar a suíte de testes de integração (test_router_e2e.py) sem precisar subir o servidor manualmente:

Com uv:
Bash
uv run pytest -v
Sem uv:
Bash
pytest -v
O Pytest vai identificar automaticamente os testes, executar o TestClient em memória e exibir o resultado das asserções e das estratégias de roteamento multi-modelo.

Com certeza! Aqui está um `README.md` completo, profissional e pronto para documentar o seu projeto/módulo base. Ele inclui a explicação da arquitetura, instruções de execução e um **diagrama visual em Mermaid** mostrando o fluxo de conexão entre as classes, configurações, servidor e suíte de testes.

Você pode criar um arquivo chamado `README.md` na raiz da pasta `open-router-connection` e colar o conteúdo abaixo:

---

# 🚀 OpenRouter Multi-Model Integration (Python Baseline)

Este repositório contém um **módulo de integração profissional e resiliente com o OpenRouter** desenvolvido em Python. Ele foi desenhado seguindo padrões modernos de engenharia de software (Clean Architecture, SOLID, Fail-Fast) para servir como **Starter Kit** reutilizável em aplicações de IA Generativa e Agentes (LangGraph / FastAPI).

---

## 🏛️ Arquitetura e Diagrama de Conexões

O diagrama abaixo ilustra como as variáveis de ambiente, as configurações Pydantic, a camada de serviço, a API FastAPI e a suíte de testes do Pytest se conectam:

```mermaid
graph TD
    %% Configuração e Ambiente
    subgraph Configuração e Validação [Startup Phase]
        ENV[".env / .env.example"] -->|Lê chaves| CFG["config.py\n(OpenRouterConfig - Pydantic Settings)"]
        CFG -->|Valida Fail-Fast| DEF_CFG["default_config\n(Instância Global Padrão)"]
    end

    %% Camada de Serviço
    subgraph Serviço Integrado [Domain / Service Layer]
        DEF_CFG -->|Injeta Config Padrão| SVC["services/openrouter_service.py\n(OpenRouterService)"]
        CLIENT["AsyncOpenAI Client\n(base_url: openrouter.ai)"] <-->|Delega Chamadas| SVC
    end

    %% Camada de Transporte (API)
    subgraph Transport Layer [FastAPI App]
        SVC -->|Injetado em| SRV["server.py\n(create_app)"]
        REQ["POST /chat\n(ChatRequest)"] --> SRV
        SRV -->|Retorna| RES["ChatResponse\n(model + content)"]
    end

    %% Servidor de Produção
    subgraph Servidor Web [Execution]
        MAIN["main.py"] -->|Instancia| SRV
        MAIN -->|Executa via| UVICORN["Uvicorn Server\n(Porta 3000)"]
    end

    %% Suíte de Testes
    subgraph Suíte de Testes [Pytest Integration]
        TST["tests/test_router_e2e.py"] -->|Override de Config\n(Price / Throughput)| TEST_SVC["OpenRouterService\n(Config Customizada)"]
        TEST_SVC -->|Injeta em| TEST_APP["FastAPI App\n(Em Memória)"]
        CLIENT_TEST["TestClient (HTTPX)"] -->|Simula Requisições| TEST_APP
    end

```

---

## 🛠️ Tecnologias e Decisões de Arquitetura

* **Pydantic Settings (`config.py`):** Garante a validação de tipos e a presença de variáveis obrigatórias (`OPENROUTER_API_KEY`) no *startup* da aplicação (*Fail-Fast*).
* **AsyncOpenAI (`services/openrouter_service.py`):** Utiliza a SDK oficial assíncrona da OpenAI apontada para o endpoint do OpenRouter, viabilizando **Roteamento Multi-Modelo** (*Price, Latency, Throughput*) com observabilidade do modelo escolhido no retorno.
* **Inversão de Dependência (SOLID):** O construtor do `OpenRouterService` aceita um `config_override`, permitindo alterar dinamicamente listas de modelos e estratégias durante os testes sem modificar arquivos em disco.
* **FastAPI + Pydantic (`server.py`):** Camada de transporte assíncrona ultrarrápida com documentação OpenAPI (`/docs`) gerada automaticamente.
* **Pytest + TestClient (`tests/test_router_e2e.py`):** Testes end-to-end simulados diretamente em memória (sem necessidade de abrir portas HTTP reais no SO).

---

## 📁 Estrutura de Arquivos

```text
.
├── .env                       # Segredos locais (Não versionado)
├── .env.example               # Contrato das variáveis de ambiente
├── config.py                  # Pydantic Settings e validação inicial
├── main.py                    # Entrypoint do servidor Uvicorn
├── server.py                  # Endpoints FastAPI e schemas de DTO
├── services/
│   ├── __init__.py
│   └── openrouter_service.py # Lógica de chamada ao OpenRouter e extração
└── tests/
    ├── conftest.py            # Resolução de caminhos sys.path
    └── test_router_e2e.py     # Testes de integração E2E com Pytest

```

---

## 🚀 Como Executar o Projeto

### 1. Configurar Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto com a sua chave da API:

```env
OPENROUTER_API_KEY=sk-or-v1-sua-chave-aqui
PORT=3000

```

### 2. Instalar Dependências (usando `uv`)

```bash
uv pip install fastapi uvicorn openai pydantic-settings pytest httpx

```

### 3. Executar o Servidor de Desenvolvimento

```bash
uv run python main.py

```

O servidor estará rodando em `http://localhost:3000`. Você pode testar os endpoints interativamente através do Swagger UI em:
👉 **`http://localhost:3000/docs`**

---

## 🧪 Executando os Testes Automatizados

Para rodar a suíte de testes de integração com validação das estratégias de roteamento:

```powershell
# No PowerShell (garantindo contexto do módulo):
$env:PYTHONPATH="."
uv run pytest -v

```

---

## 🔄 Como Reutilizar Este Módulo em Outros Projetos

Para reaproveitar esta estrutura em um novo repositório ou no seu agente LangGraph:

1. Copie o arquivo `config.py` e a pasta `services/`.
2. Importe a classe `OpenRouterService`:
```python
from services.openrouter_service import OpenRouterService

service = OpenRouterService()
resultado = await service.generate_response(
    user_message="Sua pergunta aqui...",
    system_prompt="Regras do seu agente..."
)
print(f"Modelo Respondente: {resultado['model']}")
print(f"Conteúdo: {resultado['content']}")

```