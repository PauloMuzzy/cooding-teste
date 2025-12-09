from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from utils.logger import log_error

templates = Jinja2Templates(directory="views")
router = APIRouter()


@router.get("/login/{client_uuid}", response_class=HTMLResponse)
async def get_html(request: Request):
    try:
        return templates.TemplateResponse(
            "pages/public/login.html",
            {
                "request": request,
                "title": "Entrar no Sistema",
                "client_uuid": request.path_params["client_uuid"],
            },
        )
    except Exception as e:
        print(e)
        log_error(
            mensagem=f"Erro ao baixar HTML: {str(e)}",
            contexto="login_web",
            dados_adicionais={"error": type(e).__name__},
        )
        return None
