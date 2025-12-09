from fastapi import HTTPException, Request, status
from repositories.auth_repository import AuthRepository
from utils.security import SecurityUtils

auth_repo = AuthRepository()
security = SecurityUtils()


async def get_current_client(request: Request):
    token = request.cookies.get("session_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER, headers={"Location": "/login"}
        )

    token_hash = security.hash_token(token)
    session = await auth_repo.get_session_by_token_hash(token_hash)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER, headers={"Location": "/login"}
        )

    client_uuid = session.get("uuid")

    if not session:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            headers={"Location": f"/login/{client_uuid}"},
        )

    return {
        "client_id": session["client_id"],
        "client_uuid": client_uuid,
        "client_name": session.get("name", "Cliente"),
    }
