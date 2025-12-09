from repositories.auth_repository import AuthRepository
from utils.security import SecurityUtils
from utils.logger import log_error
from datetime import datetime, timedelta
from typing import Tuple, Optional, Dict
import uuid


class AuthService:
    def __init__(self):
        self.repo = AuthRepository()
        self.sec = SecurityUtils()

    async def authenticate_client(
        self, client_uuid: str, access_code: str
    ) -> Tuple[bool, Optional[Dict], Optional[str]]:
        try:
            try:
                uuid.UUID(client_uuid)
            except ValueError:
                log_error(
                    mensagem="UUID inválido recebido na autenticação",
                    contexto="auth_service",
                    dados_adicionais={"client_uuid": client_uuid},
                )
                return False, None, "Link de acesso inválido"

            client = await self.repo.get_client_by_uuid(client_uuid)
            if not client:
                log_error(
                    mensagem="Tentativa de login com UUID inexistente",
                    contexto="auth_service",
                    dados_adicionais={"client_uuid": client_uuid},
                )
                return False, None, "Link inválido ou cliente não encontrado"

            if not client.get("is_active", False):
                log_error(
                    mensagem="Tentativa de login com cliente inativo",
                    contexto="auth_service",
                    dados_adicionais={
                        "client_id": client["id"],
                        "client_uuid": client_uuid,
                    },
                )
                return (
                    False,
                    None,
                    "Acesso temporariamente desativado. Contate o administrador.",
                )

            if not self.sec.verify_access_code(
                access_code, client["hashed_access_code"]
            ):
                log_error(
                    mensagem="Código de acesso incorreto",
                    contexto="auth_service",
                    dados_adicionais={
                        "client_id": client["id"],
                        "client_uuid": client_uuid,
                        "ip": "unknown",
                    },
                )
                return False, None, "Código de acesso inválido"
            return True, client, None

        except Exception as e:
            log_error(
                mensagem=f"Erro inesperado no authenticate_client: {str(e)}",
                contexto="auth_service",
                dados_adicionais={
                    "client_uuid": client_uuid,
                    "error_type": type(e).__name__,
                    "error": str(e),
                },
            )
            return False, None, "Erro interno do servidor. Tente novamente mais tarde."

    async def create_client_session(self, client_id: int) -> Tuple[bool, Optional[str]]:
        try:
            token = self.sec.create_secure_token()
            token_hash = self.sec.hash_token(token)
            expires_at = datetime.utcnow() + timedelta(days=30)

            await self.repo.create_session(client_id, token_hash, expires_at)
            return True, token

        except Exception as e:
            log_error(
                mensagem=f"Falha ao criar sessão para client_id {client_id}: {str(e)}",
                contexto="auth_service_session",
                dados_adicionais={"client_id": client_id, "error": type(e).__name__},
            )
            return False, None
