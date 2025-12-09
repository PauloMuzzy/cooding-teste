# repositories/auth_repository.py
from typing import Optional
from uuid import UUID
from config.database import get_db
from datetime import datetime


class AuthRepository:
    async def get_client_by_uuid(self, client_uuid: str) -> Optional[dict]:
        async with get_db() as (conn, cursor):
            cursor.execute(
                "SELECT id, uuid, name, hashed_access_code, is_active FROM clients WHERE uuid = %s",
                (client_uuid,),
            )
            return cursor.fetchone()

    async def create_session(
        self, client_id: int, token_hash: str, expires_at: datetime
    ) -> None:
        async with get_db() as (conn, cursor):
            cursor.execute(
                """
                INSERT INTO client_sessions (client_id, token_hash, expires_at)
                VALUES (%s, %s, %s)
                """,
                (client_id, token_hash, expires_at),
            )

    async def get_session_by_token_hash(self, token_hash: str) -> Optional[dict]:
        async with get_db() as (conn, cursor):
            cursor.execute(
                """
                SELECT cs.*, c.id as client_id, c.uuid, c.name
                FROM client_sessions cs
                JOIN clients c ON cs.client_id = c.id
                WHERE cs.token_hash = %s AND cs.expires_at > NOW()
                """,
                (token_hash,),
            )
            return cursor.fetchone()

    async def delete_expired_sessions(self) -> None:
        async with get_db() as (conn, cursor):
            cursor.execute("DELETE FROM client_sessions WHERE expires_at < NOW()")
