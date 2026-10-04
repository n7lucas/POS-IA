# services/preferences_service.py
import json
import aiosqlite
from typing import Optional
from models import UserPreferences


class PreferencesService:
    def __init__(self, db_path: str):
        self.db_path = db_path

    async def init_db(self):
        """Cria as tabelas de preferências e resumo no SQLite se não existirem."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS user_preferences (
                    user_id TEXT PRIMARY KEY,
                    preferences_json TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS conversation_summaries (
                    user_id TEXT PRIMARY KEY,
                    summary TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            await db.commit()

    async def get_preferences(self, user_id: str) -> Optional[UserPreferences]:
        """Obtém as preferências salvas para um usuário."""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT preferences_json FROM user_preferences WHERE user_id = ?", 
                (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row and row[0]:
                    data = json.loads(row[0])
                    return UserPreferences(**data)
        return None

    async def merge_preferences(self, user_id: str, new_pref: UserPreferences) -> UserPreferences:
        """Une incrementalmente preferências antigas com novas sem sobrescrever campos omitidos."""
        current = await self.get_preferences(user_id) or UserPreferences()

        # Atualiza nome e idade se informados
        if new_pref.name:
            current.name = new_pref.name
        if new_pref.age:
            current.age = new_pref.age

        # Mescla listas sem duplicatas
        if new_pref.favorite_genres:
            genres_set = set(current.favorite_genres + new_pref.favorite_genres)
            current.favorite_genres = list(genres_set)

        if new_pref.favorite_artists:
            artists_set = set(current.favorite_artists + new_pref.favorite_artists)
            current.favorite_artists = list(artists_set)

        # Atualiza ou concatena informações adicionais
        if new_pref.additional_info:
            if current.additional_info:
                current.additional_info += f" | {new_pref.additional_info}"
            else:
                current.additional_info = new_pref.additional_info

        # Salva no SQLite
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO user_preferences (user_id, preferences_json) 
                VALUES (?, ?)
                ON CONFLICT(user_id) DO UPDATE SET 
                    preferences_json = excluded.preferences_json,
                    updated_at = CURRENT_TIMESTAMP;
            """, (user_id, current.model_dump_json()))
            await db.commit()

        return current

    async def save_summary(self, user_id: str, summary: str):
        """Salva ou atualiza o resumo da conversa no SQLite."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO conversation_summaries (user_id, summary)
                VALUES (?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    summary = excluded.summary,
                    updated_at = CURRENT_TIMESTAMP;
            """, (user_id, summary))
            await db.commit()

    async def get_summary(self, user_id: str) -> Optional[str]:
        """Obtém o resumo armazenado para o usuário."""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT summary FROM conversation_summaries WHERE user_id = ?", 
                (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else None