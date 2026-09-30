# server.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from services.openrouter_service import OpenRouterService

# Instância global do serviço para utilização em produção
openrouter_service = OpenRouterService()

class ChatRequest(BaseModel):
    question: str = Field(..., min_length=3, description="Pergunta do utilizador")

class ChatResponse(BaseModel):
    model: str
    content: str


def create_app(service: OpenRouterService = openrouter_service) -> FastAPI:
    app = FastAPI(title="OpenRouter Integration API")

    @app.post("/chat", response_model=ChatResponse)
    async def chat_endpoint(request: ChatRequest):
        try:
            result = await service.generate_response(user_message=request.question)
            return ChatResponse(
                model=result["model"],
                content=result["content"]
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return app

