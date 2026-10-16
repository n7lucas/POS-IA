# graph/nodes.py
from typing import Optional, Union, List
from langchain_core.messages import AIMessage
from graph.state import GraphState
from models import GuardrailCheckResult, UserProfile, UserRole
from services.openrouter_service import OpenRouterService
from services.mcp_service import McpService
from prompts import get_system_prompt_template, get_blocked_prompt_template


def _extract_text(content: Union[str, List]) -> str:
    """Garante extração limpa de texto."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for b in content:
            if isinstance(b, str):
                parts.append(b)
            elif isinstance(b, dict) and b.get("type") == "text":
                parts.append(b.get("text", ""))
        return " ".join(parts)
    return str(content) if content else ""


def _parse_user(state: GraphState) -> UserProfile:
    """Obtém o usuário do estado ou fallback para testes no LangGraph Studio."""
    raw = state.get("user")
    if isinstance(raw, UserProfile):
        return raw
    if isinstance(raw, dict):
        return UserProfile(**raw)
    # Default equivalente ao state.user = getUser('ananeri') no TypeScript
    return UserProfile(display_name="Ana Neri", role=UserRole.MEMBER)


def create_guardrails_check_node(open_router_service: OpenRouterService):
    async def guardrails_check_node(state: GraphState) -> dict:
        try:
            messages = state.get("messages", [])
            user_prompt = _extract_text(messages[-1].content) if messages else ""
            user = _parse_user(state)
            guardrails_enabled = state.get("guardrailsEnabled", True)

            # Formata o System Prompt com a role e nome do usuário
            system_template = get_system_prompt_template()
            system_prompt = system_template.format(
                USER_ROLE=user.role.value,
                USER_NAME=user.display_name
            )

            # Junta o contexto do usuário com o prompt da mensagem
            msg = f"{system_prompt}\n{user_prompt}"

            # Valida com o modelo de Guardrail
            result = await open_router_service.check_guardrails(
                msg=msg, 
                enabled=guardrails_enabled
            )

            return {"guardrailCheck": result}
        except Exception as e:
            return {
                "guardrailCheck": GuardrailCheckResult(
                    safe=False,
                    reason="Serviço de guardrails indisponível - requisição bloqueada por segurança.",
                    analysis=str(e)
                )
            }
    return guardrails_check_node


def create_chat_node(open_router_service: OpenRouterService, mcp_service: McpService):
    async def chat_node(state: GraphState) -> dict:
        try:
            messages = state.get("messages", [])
            user_prompt = _extract_text(messages[-1].content) if messages else ""
            user = _parse_user(state)

            system_template = get_system_prompt_template()
            system_prompt = system_template.format(
                USER_ROLE=user.role.value,
                USER_NAME=user.display_name
            )

            # Obtém as ferramentas MCP do Filesystem
            tools = await mcp_service.get_tools()

            # Gera a resposta utilizando o executor com as ferramentas
            response_text = await open_router_service.generate(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                tools=tools
            )

            return {"messages": [AIMessage(content=response_text)]}
        except Exception as e:
            return {
                "messages": [AIMessage(content="Ocorreu um erro ao processar sua requisição.")]
            }
    return chat_node


async def blocked_node(state: GraphState) -> dict:
    check = state.get("guardrailCheck")
    user = _parse_user(state)

    reason = check.reason if check and check.reason else "Falha na verificação de segurança."
    analysis = f"Análise: {check.analysis}" if check and check.analysis else ""
    permissions = ", ".join(user.permissions) if hasattr(user, 'permissions') and user.permissions else "Nenhuma"

    blocked_template = get_blocked_prompt_template()
    blocked_message = blocked_template.format(
        REASON=reason,
        ANALYSIS=analysis,
        USER_ROLE=user.role.value,
        PERMISSIONS=permissions
    )

    return {"messages": [AIMessage(content=blocked_message)]}


def route_after_guardrails(state: GraphState) -> str:
    """Condição idêntica ao edgeConditions.ts."""
    if not state.get("guardrailsEnabled", True):
        return "chat"

    check = state.get("guardrailCheck")
    if not check or check.safe:
        return "chat"

    return "blocked"