# services/openrouter_service.py
from typing import List
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.tools import BaseTool
from models import GuardrailCheckResult
from prompts import get_guardrail_prompt_template
from config import settings


class OpenRouterService:
    def __init__(self):
        # Utiliza a chave da OpenAI com gpt-4o-mini para execuções sem erro 400 da API
        self.client = ChatOpenAI(
            model=settings.default_model,
            temperature=0.0,
            openai_api_key=settings.openai_api_key,
        )

    async def check_guardrails(self, msg: str, enabled: bool = True) -> GuardrailCheckResult:
        if not enabled:
            return GuardrailCheckResult(safe=True, reason="Guardrails desabilitados.", analysis="Bypass ativo.")

        prompt_template = get_guardrail_prompt_template()
        messages = prompt_template.format_messages(user_input=msg)

        runnable = self.client.with_structured_output(GuardrailCheckResult)
        try:
            return await runnable.ainvoke(messages)
        except Exception as e:
            return GuardrailCheckResult(
                safe=False, 
                reason="Falha na verificação do Guardrail.", 
                analysis=str(e)
            )

    async def generate(self, system_prompt: str, user_prompt: str, tools: List[BaseTool]) -> str:
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]

        # Se houver ferramentas, vincula ao cliente
        llm = self.client.bind_tools(tools) if tools else self.client
        
        # Executa a chamada
        response = await llm.ainvoke(messages)

        # Se a LLM respondeu com uma Tool Call (ex: leu o arquivo via MCP), executamos a chamada
        if getattr(response, "tool_calls", None):
            tool_call = response.tool_calls[0]
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]

            # Localiza a ferramenta correspondente do MCP
            selected_tool = next((t for t in tools if t.name == tool_name), None)
            if selected_tool:
                tool_output = await selected_tool.ainvoke(tool_args)
                
                # Devolve o resultado lido do arquivo para o modelo gerar a resposta textual
                final_messages = messages + [response, tool_output]
                final_response = await self.client.ainvoke(final_messages)
                return str(final_response.content)

        return str(response.content)