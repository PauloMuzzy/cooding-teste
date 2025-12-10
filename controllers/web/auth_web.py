from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from utils.logger import log_error

templates = Jinja2Templates(directory="views")
router = APIRouter()

@router.get("/login", response_class=HTMLResponse)
async def login_without_uuid(request: Request):
    try:
        return templates.TemplateResponse(
            "pages/public/invalid_link.html",
            {"request": request}
        )
    except Exception as e:
        log_error(
            mensagem=f"Erro ao baixar HTML: {str(e)}",
            contexto="invalid_link",
            dados_adicionais={"error": type(e).__name__},
        )
    return None

@router.get("/login/{client_uuid}", response_class=HTMLResponse)
async def get_login_page(request: Request, client_uuid: str):
    try:
        return templates.TemplateResponse(
            "pages/public/login.html",
            {
                "request": request,
                "client_uuid": client_uuid,
            }
        )
    except Exception as e:
        log_error(
            mensagem=f"Erro ao baixar HTML: {str(e)}",
            contexto="login_web",
            dados_adicionais={"error": type(e).__name__},
        )
    return None
