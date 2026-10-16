# Aula 1: Conhecendo o template, arquitetura e definição do projeto.

## Passo 1 Estrutura do Projeto e Dependências

```python

rag-neo4j-python/
├── .env
├── config.py
├── services/
│   ├── __init__.py
│   ├── llm_service.py
│   └── neo4j_service.py
├── prompts/
│   └── __init__.py
├── graph/
│   ├── __init__.py
│   ├── state.py
│   ├── builder.py
│   └── nodes/
│       ├── __init__.py
│       └── extract_question.py
└── main.py

```

### Instalação de dependências necessárias
```

uv pip install langchain langchain-openai langchain-community langgraph pydantic pydantic-settings neo4j

```
## Passo 2: Configurações Globais

No **TypeScript**, o professor usou um objeto exportado config. Em **Python**, a forma mais robusta e idiomática de gerenciar variáveis de ambiente e configurações é usando o ``pydantic-settings``. Crie o seu arquivo ``.env`` com as chaves e, em seguida, crie o`` config.py``:

## Passo 3: O Estado do Grafo (graph/state.py)

No TypeScript, o estado foi definido com **Zod** **(SalesStateAnnotation)**. No Python, o LangGraph utiliza **TypedDict** para definir o formato do estado. Cada campo aqui representará uma peça de informação que transitará entre os nós (como os resultados intermediários ou a query gerada).

## Passo 4: O Primeiro Nó - Extract Question (graph/nodes/extract_question.py)

O objetivo deste nó é simples, mas crucial: ele olha para o histórico de mensagens, extrai o último texto enviado pelo usuário e o coloca no campo **question** do estado. Se o **messages** estiver vazio, ele sinaliza um erro. Isso evita que os próximos nós precisem ficar vasculhando o array de mensagens.

# Aula 2: Query Planner Node — Análise de Complexidade e Decomposição.

Nesta etapa, nosso objetivo é imitar o raciocínio humano diante de uma pergunta. Se a pergunta for simples ("Liste todos os cursos"), o fluxo segue reto. Se for complexa ("Quais cursos são normalmente comprados juntos?"), o planejador vai quebrar a pergunta original em subquestions menores para serem resolvidas passo a passo.

Para isso funcionar no Python, precisamos de 3 componentes:

* O serviço de LLM configurado para retornar dados estruturados (JSON).

* O prompt e o Schema de extração do planejador (usando Pydantic no lugar do Zod).

* O nó do LangGraph (query_planner) para atualizar o estado.

## Passo 1: O Serviço de LLM (services/llm_service.py)

No TypeScript, o professor usou llmClient.generateStructured. No LangChain Python, a função equivalente e mais poderosa é o .with_structured_output(). Crie o serviço para abstrair a chamada à LLM:

## Passo 2: O Schema Pydantic e os Prompts (prompts/query_analyzer.py)

No arquivo TypeScript original, o Zod foi usado para forçar a saída (complexity, requiresDecomposition, etc). Aqui usamos o **BaseModel** do Pydantic, que serve nativamente de contrato para o **.with_structured_output()** do passo anterior.

## Passo 3: O Nó do Planejador (graph/nodes/query_planner.py)   
A lógica de engenharia de software da Aula 2 dita o seguinte: nunca confie cegamente, e se der erro, não trave. Se a IA falhar em planejar, assumimos que é uma requisição "simples" e deixamos o fluxo tentar resolver com apenas 1 query.

# Aula 3: Cypher Generator e Integração com Neo4j

Nesta etapa, o nosso sistema vai pegar a pergunta (ou a subquestion da etapa atual) e transformá-la numa consulta na linguagem do banco de dados em grafos (Cypher). Para que o modelo de IA acerte a query, nós não podemos deixá-lo adivinhar. Precisamos injetar o Schema real do banco e o Contexto de Negócio diretamente no prompt dele.

Precisaremos de 4 arquivos para isso:

1. O Serviço de Conexão com o Neo4j.

2. O Contexto de Negócio.

3. O Schema e Prompts do Gerador.

4. O Nó do Grafo que gera a query.

## Passo 1: O Serviço do Neo4j (services/neo4j_service.py)
No Python, vamos utilizar o Neo4jGraph da biblioteca langchain_community. Para não bloquear nosso código assíncrono (já que o driver base do LangChain para o Neo4j é síncrono), vamos envelopar as chamadas de I/O em asyncio.to_thread. Isso garante performance!


## Passo 2: O Contexto de Negócios e o Prompt (prompts/sales_context.py e prompts/cypher_generator.py)

Crie o arquivo com as regras de negócio. Isso evita que o modelo conte matrículas canceladas como receita, por exemplo.

## Passo 3: O Nó Cypher Generator (graph/nodes/cypher_generator.py)

Este nó pega as dependências, decide qual pergunta processar (a original ou a do step atual), injeta o banco de dados no prompt e gera a query.

# Aula 4: Cypher Executor — Validando e Executando Queries no Neo4j.

Nesta etapa, assumimos a mentalidade da Engenharia de Software Defensiva: Nós nunca confiamos cegamente na primeira query gerada pelo modelo.

1. Primeiro, rodamos um comando EXPLAIN no banco. Se a sintaxe estiver quebrada, o banco nos avisa sem tentar alterar nada.

2. Se falhar, preparamos o estado para autocorreção (needs_correction = True).

3. Se funcionar, executamos de verdade. Se for uma requisição Multi-step, nós guardamos o resultado no histórico (sub_results), avançamos o passo (current_step + 1) e devolvemos o fluxo para a LLM gerar a próxima query.

## Passo 1: O Nó Cypher Executor (graph/nodes/cypher_executor.py)
Crie o arquivo abaixo. Preste muita atenção em como manipulamos o dicionário de estado (state), pois é aqui que a orquestração do loop Multi-step acontece de fato.

# Aula 5, o último passo para transformar dados brutos em inteligência artificial aplicada.

Esta aula é dividida em duas responsabilidades distintas:

1. O Cypher Correction: Onde injetamos o erro recebido do banco de dados na LLM e pedimos para ela consertar a sintaxe da query.

2. A Analytical Response: Onde consolidamos todos os dados, tabelas ou passos múltiplos em uma resposta rica, humanizada e com sugestões de próximas perguntas (Follow-ups).

Vamos começar implementando os prompts e os schemas.

## Passo 1: Prompts de Correção e Resposta Analítica

Crie os dois arquivos de prompts abaixo na sua pasta **prompts/**. Note que o **AnalyticalResponse** tem diferentes templates de acordo com o cenário (Erro, Sem Resultados, Sucesso Simples ou Sucesso Multi-step).

## Passo 2: Os Nós de Correção e Síntese
Agora, criamos os nós na pasta graph/nodes/.

O nó de Resposta Analítica tem um detalhe muito importante do LangGraph: ele retorna uma chave messages contendo um objeto AIMessage. Isso permite que o LangGraph guarde o histórico da conversa naturalmente!



---

# 📊 Agente Analítico RAG Avançado com Neo4j & LangGraph

Este repositório contém a implementação em **Python** de uma arquitetura de **RAG (Retrieval-Augmented Generation) Avançado utilizando Banco de Dados em Grafos (Neo4j)**. Em vez de utilizar busca semântica em vetores para responder perguntas com textos não estruturados, este projeto converte linguagem natural em consultas estruturadas (Cypher) para extrair dados relacionais precisos e gerar *insights* de negócios.

O sistema atua como um analista de dados autônomo, capaz de planejar decomposições multi-step para perguntas complexas, validar suas próprias consultas, corrigir erros de sintaxe automaticamente e sintetizar os dados em respostas humanizadas.

## 🏗️ Arquitetura e Fluxo de Execução

O coração do projeto é uma Máquina de Estados (*State Machine*) construída com **LangGraph**, operando de forma cíclica e determinística.

```text
===================================================================================
                         PIPELINE ANALÍTICO - LANGGRAPH
===================================================================================

 [ Entrada do Usuário ]
          |
          v
 +--------------------+
 |  extract_question  | ---> (Extrai intenção e limpa a entrada)
 +---------+----------+
          |
          v
 +--------------------+
 |   query_planner    | ---> (Classifica: Simples vs Complexa. Decompõe em passos)
 +---------+----------+
          |
          v
 +--------------------+
 |  cypher_generator  | <-----------------------------------------+
 +---------+----------+                                           |
          | (Injeta Schema + Regras de Negócio -> Gera Cypher)    |
          v                                                       |
 +--------------------+                                     [ Próximo Passo ]
 |  cypher_executor   | ---> (Valida via EXPLAIN e Executa)       |
 +---------+----------+                                           |
          |                                                       |
   +------+------+------------------------------------------------+
   |             |                                                |
[Erro]       [Sucesso]                                        [Sucesso]
   |             |                                                |
   v             v                                                |
 +--------------------+       +--------------------+              |
 | cypher_correction  |       |  Multi-step Loop   | -------------+
 +---------+----------+       +--------+-----------+ (Se houver sub-perguntas)
   |       |                           |
   +-------+                           | (Se concluído ou Simples)
 (Conserta e Retenta)                  v
                              +--------------------+
                              | analytical_response| ---> (Sintetiza em texto)
                              +---------+----------+
                                        |
                                        v
                                 [ Resposta Final ]

```

## ✨ Principais Funcionalidades

* **Query Planner (Decomposição):** Capacidade de identificar perguntas complexas (ex: *"Compare a receita entre cursos de alta e baixa conclusão"*) e dividi-las em sub-perguntas lógicas (*Multi-step reasoning*).
* **Engenharia de Prompt Defensiva:** Injeção dinâmica do *Schema* atualizado do Neo4j e do Contexto de Negócios para garantir a precisão da linguagem Cypher gerada.
* **Validação Antes da Execução:** Utilização do comando `EXPLAIN` no Neo4j para validar a sintaxe da consulta antes de qualquer tentativa real de leitura ou processamento.
* **Autocorreção em Loop (Self-Healing):** Se a query gerada for inválida, o nó de correção analisa a mensagem de erro do banco de dados, reescreve a query e tenta novamente (com limite configurável de tentativas para evitar *loops* infinitos).
* **Geração Estruturada (Pydantic):** Uso estrito de `Structured Outputs` para garantir que as transições de estado do grafo operem com tipagem forte e previsível.

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3.12+
* **Orquestração de Grafos:** LangGraph
* **Framework de LLM:** LangChain
* **Validação e Tipagem:** Pydantic V2
* **Banco de Dados em Grafos:** Neo4j (via Docker)
* **Provedor de Modelos:** OpenRouter / OpenAI API

## 📁 Estrutura do Projeto

```text
.
├── docker-compose.yml            # Infraestrutura local do banco de dados
├── config.py                     # Configurações globais e variáveis de ambiente
├── main.py                       # Interface interativa de linha de comandos (CLI)
├── services/
│   ├── llm_service.py            # Integração com modelos e extração estruturada
│   └── neo4j_service.py          # Conexão, validação (EXPLAIN) e queries ao banco
├── prompts/
│   ├── analytical_response.py    # Templates de síntese e follow-ups
│   ├── cypher_correction.py      # Templates de autocorreção baseada em erros
│   ├── cypher_generator.py       # Templates de conversão NL-to-Cypher
│   ├── query_analyzer.py         # Avaliação de complexidade
│   └── sales_context.py          # Regras de negócios do domínio
└── graph/
    ├── state.py                  # Definição do TypedDict (GraphState)
    ├── builder.py                # Fábrica do LangGraph e roteamento condicional
    └── nodes/                    # Lógica isolada de cada etapa do pipeline

```

## 🚀 Como Executar Localmente

### 1. Pré-requisitos

* **Python 3.12+** instalado.
* **Docker** e **Docker Compose** instalados (para o banco Neo4j).
* Um gerenciador de dependências como `uv` ou `pip`.

### 2. Configurar Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto com as suas credenciais:

```env
OPENAI_API_KEY=sk-sua-chave-aqui
DEFAULT_MODEL=gpt-4o-mini
NEO4J_URI=neo4j://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

```

### 3. Subir o Banco de Dados (Neo4j)

Inicie o contêiner Docker contendo o banco de dados em grafos:

```bash
docker compose up -d

```

*(Nota: Para que as consultas retornem dados reais, certifique-se de popular o banco executando o script de Seed fornecido no repositório base).*

### 4. Instalar as Dependências

```bash
uv pip install langchain langchain-openai langchain-community langgraph pydantic pydantic-settings neo4j

```

### 5. Executar o Agente

Inicie o terminal interativo para conversar com os dados:

```bash
uv run python main.py

```

## 🧪 Exemplos de Interação

**Cenário Simples:**

> *Usuário:* "Quais são os cursos disponíveis na plataforma?"
> *Sistema:* Gera 1 query, executa, resume os dados e sugere próximas perguntas.

**Cenário Complexo (Multi-step):**

> *Usuário:* "Quais cursos são normalmente comprados juntos?"
> *Sistema:* O *Planner* divide a pergunta, gera múltiplas queries lógicas, acumula os resultados iterativamente e sintetiza um panorama correlacional das compras.