# prompts.py
from typing import Optional
from models import UserPreferences


def get_chat_system_prompt(user_context: Optional[UserPreferences], conversation_summary: Optional[str]) -> str:
    context_str = ""
    if user_context:
        details = []
        if user_context.name: details.append(f"Nome: {user_context.name}")
        if user_context.age: details.append(f"Idade: {user_context.age}")
        if user_context.favorite_genres: details.append(f"Gêneros Favoritos: {', '.join(user_context.favorite_genres)}")
        if user_context.favorite_artists: details.append(f"Artistas Favoritos: {', '.join(user_context.favorite_artists)}")
        if user_context.additional_info: details.append(f"Outros Detalhes: {user_context.additional_info}")
        context_str = "\n".join(details)
    else:
        context_str = "Nenhuma preferência registrada ainda."

    summary_str = conversation_summary if conversation_summary else "Nenhum resumo anterior."

    return f"""Você é um assistente especialista e recomendador de músicas caloroso e amigável.
Sua missão é conversar com o usuário sobre música, recomendar artistas e bandas, e aprender sobre suas preferências.

CONTEXTO DO USUÁRIO (Memória de Longo Prazo):
{context_str}

RESUMO DA CONVERSA ANTERIOR:
{summary_str}

DIRETRIZES:
1. Responda sempre em português de forma natural e envolvente.
2. Utilize o CONTEXTO DO USUÁRIO para personalização (ex: se ele for surfista ou gostar de rock, ajuste suas recomendações).
3. Se o usuário mencionar novas preferências (nome, gêneros, bandas favoritas, hobbies), defina 'should_save_preferences' como True e preencha 'extracted_preferences'.
4. Caso contrário, defina 'should_save_preferences' como False.
"""


def get_summarize_system_prompt(previous_summary: Optional[str]) -> str:
    prev_str = f"RESUMO ANTERIOR:\n{previous_summary}" if previous_summary else "Nenhum resumo anterior."

    return f"""Você é um analisador de contexto para compactação de histórico de conversas.
Sua tarefa é criar ou atualizar um resumo conciso e incremental das interações entre o usuário e o assistente de música.

{prev_str}

REGRAS DE RESUMO:
1. Mantenha apenas os fatos e tópicos essenciais mencionados (estilos musicais citados, opiniões sobre bandas, rotinas).
2. Não perca informações de perfil pessoal (ex: se o usuário disse que estuda à noite ou curte reggae).
3. Consolide informações repetidas para economizar tokens.
4. O resumo deve ser escrito de forma clara em português.
"""