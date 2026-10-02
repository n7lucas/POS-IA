# server.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage

from graph.builder import build_graph, app_graph

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="Texto livre da solicitação do usuário")

class ChatResponse(BaseModel):
    intent: str
    action_success: bool
    action_error: str | None
    output: str

def create_app(compiled_graph=None) -> FastAPI:
    app = FastAPI(title="Appointment Agent API")
    graph = compiled_graph or app_graph

    @app.post("/chat", response_model=ChatResponse)
    async def chat_endpoint(request: ChatRequest):
        try:
            # Estado Inicial Limpo e Previsível
            initial_state = {
                "messages": [HumanMessage(content=request.message)],
                "intent": "unknown",
                "professional_id": None,
                "professional_name": None,
                "date_time": None,
                "patient_name": None,
                "reason": None,
                "action_success": False,
                "action_error": None,
                "output": ""
            }

            # Invocação Assíncrona do Grafo
            final_state = await graph.ainvoke(initial_state)

            return ChatResponse(
                intent=final_state.get("intent", "unknown"),
                action_success=final_state.get("action_success", False),
                action_error=final_state.get("action_error"),
                output=final_state.get("output", "")
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return app

app = create_app()