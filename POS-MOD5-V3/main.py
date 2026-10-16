# main.py
import asyncio
from langchain_core.messages import HumanMessage
from graph.builder import create_graph
from models import UserProfile, UserRole
from services.mcp_service import McpService


async def main():
    print("==========================================================")
    print("🛡️ SAFEGUARD & PROMPT INJECTION PREVENTION SYSTEM")
    print("==========================================================\n")

    print("Selecione o perfil:")
    print("1. Admin (Acesso permitido ao Filesystem)")
    print("2. Member (Acesso bloqueado ao Filesystem)")
    choice = input("Opção [1 ou 2]: ").strip()

    role = UserRole.ADMIN if choice == "1" else UserRole.MEMBER
    user_profile = UserProfile(display_name="Lucas", role=role)

    mcp_service = McpService(root_dir=".")
    graph = await create_graph(services={"mcp_service": mcp_service})

    print(f"\nSessão iniciada como '{user_profile.display_name}' ({user_profile.role.value.upper()}).\n")

    try:
        while True:
            user_input = input("Você: ").strip()
            if not user_input or user_input.lower() in ["sair", "exit"]:
                break

            input_state = {
                "messages": [HumanMessage(content=user_input)],
                "user_profile": user_profile,
                "guardrails_enabled": True,
            }

            final_state = await graph.ainvoke(input_state)
            last_msg = final_state["messages"][-1].content
            print(f"\nAssistente: {last_msg}\n")

    finally:
        await mcp_service.close()


if __name__ == "__main__":
    asyncio.run(main())