from fastapi import APIRouter, Form, HTTPException, status
from fastapi.responses import JSONResponse
from uuid import UUID
from services.auth_service import AuthService

from utils.security import SecurityUtils

router = APIRouter(prefix="/api/v1", tags=["API - Auth"])

auth_service = AuthService()


@router.post("/login/{client_uuid}")
async def api_login(client_uuid: UUID, access_code: str = Form(...)):
    success, client, error_msg = await auth_service.authenticate_client(
        str(client_uuid), access_code
    )

    if not success:
        raise HTTPException(status_code=401, detail=error_msg or "Acesso negado")

    session_ok, token = await auth_service.create_client_session(client["id"])
    if not session_ok:
        raise HTTPException(status_code=500, detail="Erro ao criar sessão")

    response = JSONResponse({"success": True})

    response.set_cookie(
        key="session_token",
        value=token,
        httponly=True,
        secure=True,  #
        samesite="strict",
        max_age=30 * 24 * 60 * 60,
        path="/",
    )
    return response
