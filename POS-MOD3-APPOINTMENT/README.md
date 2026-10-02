# Evolução do Projeto

## Aula 1 

(Visão Geral & Fluxo): Entrada em linguagem natural $\rightarrow$ Structured Output (JSON) $\rightarrow$ Lógica Determinística de Negócio no Serviço $\rightarrow$ Geração de Resposta Humana.

## Aula 2 
(Structured JSON & Integrations): Uso de Structured Outputs com Pydantic, serviço desacoplado de LLM com suporte a OpenRouter, injeção de lista de profissionais e data atual no prompt.

## Aula 3
 (Caso de Teste Schedule E2E): Implementação e teste defensivo do nó identify_intent, isolando a IA para gerar apenas a extração estruturada e lidando com falhas (fallback para unknown).

## Aula 4 

(Ações Reais, Safe Parsing e Message Generator): Nó de agendamento e nó de cancelamento com validação defensiva (safeParse via Pydantic), injeção de dependências (AppointmentService e OpenRouterService), geração de resposta final orientada a estado (action_success, action_error) e observabilidade com tracing.

# Solução idiomática em Python

* Parte 1: Camada de Configuração (config.py), Modelos e Schemas Pydantic (models.py) e Serviço de Negócio (services/appointment_service.py).

* Parte 2: Serviço LLM com Structured Output (services/openrouter_service.py), Prompts Centralizados (prompts.py), Estado (graph/state.py) e Nós do Grafo com Validação Defensiva (graph/nodes.py).

* Parte 3: Montagem da Factory do Grafo (graph/builder.py), Servidor FastAPI (server.py), langgraph.json e Testes End-to-End Automatizados (tests/test_appointment_e2e.py).

Aqui está o `README.md` completo, no padrão de arquitetura de software profissional, detalhando cada nó, classe, serviço e a relação direta com o conteúdo das Aulas 1 a 4.

Você pode criar o arquivo **`README.md`** na raiz do projeto `POS-MOD3-APPOINTMENT` e colar o código abaixo:

```markdown
# 🏥 Appointment Scheduling Agent (LangGraph + FastAPI + OpenRouter)

Um agente transacional orientado a estados (*State-Driven Flow*) desenvolvido em Python, LangChain e LangGraph para agendamento e cancelamento de consultas médicas em linguagem natural.

---

## 🎯 Objetivo e Relação com o Conteúdo do Curso

| Aula | Título da Aula | Escopo e Conceitos Implementados neste Repositório |
|---|---|---|
| **Aula 1** | *Identificando a intenção de usuários e marcando consultas médicas* | Introdução ao padrão de **Agente Transacional**. O modelo de IA não executa regras de negócio; ele atua estritamente na extração de dados e intenção em formato estruturado (JSON), deixando a execução para serviços determinísticos (`AppointmentService`). |
| **Aula 2** | *Structured JSON + JSON Prompts* | Integração do **OpenRouter** com SDK OpenAI usando `.with_structured_output()`. Injeção de contexto no prompt (data atual e lista de médicos) para resolução de datas relativas (*"amanhã"*, *"próxima quinta"*). |
| **Aula 3** | *Transformando intenção de usuários em JSON e E2E Test* | Implementação defensiva do nó `identify_intent` com suporte a *fallback* gracioso (`intent: unknown`) em caso de exceções/erros de API. Testes automatizados evoluindo para validação do corpo da resposta. |
| **Aula 4** | *Cancelando consultas a partir de texto e último teste E2E* | Padrão **"Confio, mas confiro"** (validação defensiva via Pydantic *safeParse* nos nós de ação `scheduler` e `canceller`). Nó `message_generator` para humanização final da resposta e suporte ao LangGraph Studio com Tracing ativado. |

---

## 📊 Arquitetura do Grafo (ASCII Diagram)

```text
==================================================================================================
                     SISTEMA DE AGENDAMENTO TRANSACTIONAL AGENT (COMPLETO)
==================================================================================================

 [ Usuário / HTTP Client ]
             |
             v
 [ POST /chat (server.py) ]
             |
             v
 [ StateGraph (graph/builder.py) ] <--- Injeta OpenRouterService & AppointmentService
             |
             v
   +--------------------+
   |  identify_intent   | <--- Generates Structured Output (Pydantic Schema)
   +---------+----------+      Injeta lista de Médicos + Data Atual no System Prompt
             |
             v
      /------+------\
     / route_intent  \
    +-----------------+
     /       |       \
 (schedule)  | (cancel)\ (unknown)
    v        v          v
 +------+ +------+  +----------+
 |sched.| |cancel|  | fallback | <--- Valida Payload Secundário (Pydantic / "Confio mas confiro")
 +--+---+ +--+---+  +----+-----+      Executa Lógica Determinística no AppointmentService
    |        |           |            Atualiza no Estado: action_success / action_error
    \--------+-----------/
             |
             v
 +----------------------+
 |  message_generator   | <--- Gera Texto Final Humanizado em Português
 +-----------+----------+      usando FinalMessageSchema e apenas o contexto do resultado
             |
             v
          [ END ]

```

---

## 🧱 Responsabilidade das Classes e Módulos

```text
.
├── config.py                       # Pydantic Settings (Validação Fail-Fast das chaves e parâmetros)
├── models.py                       # Schemas Pydantic (Entities e Contratos de Structured Output)
├── prompts.py                      # Prompts dinâmicos (Injeção de data atual e lista de médicos)
├── server.py                       # Servidor FastAPI expondo endpoint /chat
├── langgraph.json                  # Arquivo de configuração do LangGraph Studio / CLI
├── services/
│   ├── appointment_service.py     # Serviço determinístico (Lógica pura de agendar e cancelar)
│   └── openrouter_service.py      # Camada de comunicação LLM com .with_structured_output()
├── graph/
│   ├── state.py                   # Declaração do TypedDict GraphState (redução via add_messages)
│   ├── nodes.py                   # Funções dos nós com validação defensiva interna
│   └── builder.py                 # Factory do grafo com Inversão de Dependências (partial)
└── tests/
    └── test_appointment_e2e.py    # Suíte de testes integrados e E2E com Pytest

```

### Detalhamento dos Componentes Core:

1. **`config.py` (`Settings`):** Centraliza variáveis de ambiente (.env) e garante validação de tipos antes da aplicação ligar.
2. **`models.py` (`IntentExtractionSchema` & `FinalMessageSchema`):** Define os contratos formais que a LLM é obrigada a retornar, prevenindo alucinações de campos.
3. **`services/appointment_service.py` (`AppointmentService`):** Mantém a tabela em memória de profissionais e agendamentos. Dispara exceções de domínio caso ocorra conflito de horários ou agendamento inexistente.
4. **`services/openrouter_service.py` (`OpenRouterService`):** Abstrai as chamadas de modelo com suporte ao OpenRouter via API OpenAI, encapsulando `.with_structured_output()`.
5. **`graph/nodes.py` (`scheduler_node` / `canceller_node`):** Aplicam a validação defensiva ("confio, mas confiro") nos dados extraídos do estado usando Pydantic antes de invocar os métodos do serviço.
6. **`graph/builder.py` (`build_graph`):** Fábrica responsável por montar as arestas condicionais e injetar as instâncias de serviços nos nós via `functools.partial`.

---

## 🚀 Como Executar o Projeto

### 1. Pré-requisitos e Variáveis de Ambiente

Crie um arquivo `.env` na raiz do repositório baseado no exemplo abaixo:

```env
OPENROUTER_API_KEY=sk-or-v1-sua-chave-aqui
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=lsv2_pt_sua_chave_aqui
LANGCHAIN_PROJECT=appointment-agent
PORT=3000

```

### 2. Executar os Testes Automatizados (Pytest)

Para rodar a suíte de testes de integração e validar as regras de agendamento, cancelamento, conflito e fallback:

```powershell
$env:PYTHONPATH="."
uv run pytest -v

```

### 3. Executar a API Web (FastAPI)

```powershell
$env:PYTHONPATH="."
uv run python -m uvicorn server:app --reload --port 3000

```

Acesse a documentação interativa das APIs (Swagger UI) em:
👉 **`http://localhost:3000/docs`**

### 4. Visualizar no LangGraph Studio

Para depurar e acompanhar a execução do estado nó a nó em tempo real:

```powershell
$env:PYTHONPATH="."
uv run langgraph dev --host 127.0.0.1 --port 2024 --allow-cors "*"

```

Acesse a interface no seu navegador:
👉 **`http://127.0.0.1:2024`**

```

```