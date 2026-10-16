# Explanations related to syncronous function wraping a async funtion

This pattern is called a **Factory Function** creating a **Closure**. It is widely used in graph-based AI frameworks (like LangGraph) for **Dependency Injection**.

Here is exactly what is happening, why it is designed this way, and how to test it in your CI/CD pipeline.

### Why mix a normal function with an async function?

Frameworks that orchestrate AI agents usually expect your node functions to have a very strict signature—they only want to pass the `state` to the function:
`async def my_node(state: GraphState)`

However, your node needs access to external tools, like your `LLMService`, to actually do its job.

Instead of relying on messy global variables, the normal synchronous function acts as a wrapper. It takes the `llm_service`, "remembers" it, and returns the inner async function. The inner async function now has access to both the `state` (passed by the graph framework) and the `llm_service` (injected by the outer function).

* **Outer function (`create_query_planner_node`):** Synchronous because it only defines and returns a function object in memory. No network calls happen here.
* **Inner function (`query_planner_node`):** Asynchronous (`async`) because it handles the actual execution, including waiting for the external LLM API (`await llm_service.generate_structured`).

### How to execute it in your code

When wiring up your graph, you call the outer function normally to generate the node, and hand that generated node to the framework:

```python
# 1. Initialize your service (Synchronous)
my_llm = LLMService(api_key="...")

# 2. Call the normal function to generate the async node (Synchronous)
planner_node_func = create_query_planner_node(my_llm)

# 3. The graph framework handles executing the async function later
# result = await planner_node_func(current_state)

```

### How to write a Unit Test for this (for your CI/CD)

Testing nested async functions requires breaking the process into two steps: getting the inner function, then `await`ing it using a mocked service. You will need `pytest-asyncio` installed.

Here is how you would test this specific node to ensure your pipeline passes:

```python
import pytest
from unittest.mock import AsyncMock, MagicMock

# Import your actual code
# from graph.nodes.query_planner import create_query_planner_node

@pytest.mark.asyncio
async def test_query_planner_simple_query():
    # 1. Setup Mock State
    mock_state = {"question": "What is Python?"}
    
    # 2. Setup Mock LLM Service
    mock_llm_service = MagicMock()
    # Mock the specific async method to return (data, error)
    mock_data = MagicMock(requires_decomposition=False)
    mock_llm_service.generate_structured = AsyncMock(return_value=(mock_data, None))
    
    # 3. Call the outer sync function to get the async closure
    node_func = create_query_planner_node(mock_llm_service)
    
    # 4. Await the inner async function
    result = await node_func(mock_state)
    
    # 5. Assertions
    assert result["is_multistep"] is False
    mock_llm_service.generate_structured.assert_awaited_once()

@pytest.mark.asyncio
async def test_query_planner_missing_question():
    mock_state = {} # Empty state
    mock_llm_service = MagicMock()
    
    node_func = create_query_planner_node(mock_llm_service)
    result = await node_func(mock_state)
    
    assert "error" in result
    assert result["error"] == "Nenhuma pergunta no estado para analisar."
    # Ensure LLM was never called
    mock_llm_service.generate_structured.assert_not_called()

```