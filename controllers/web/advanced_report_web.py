from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from utils.logger import log_error
from dependencies.auth_dependency import get_current_client

templates = Jinja2Templates(directory="views")
router = APIRouter()

@router.get("/relatorio-avancado", response_class=HTMLResponse)
async def get_html(
    request: Request, client_session: dict = Depends(get_current_client)
):
    client_uuid = client_session["client_uuid"]
    try:
        return templates.TemplateResponse(
            "pages/auth/advanced_report.html",
            {
                "request": request,
                "title": "Relatório Avançado",
                "client_uuid": client_uuid,
            },
        )
    except Exception as e:
        print(e)
        log_error(
            mensagem=f"Erro ao baixar HTML: {str(e)}",
            contexto="advanced_report_web",
            dados_adicionais={"error": type(e).__name__},
        )
        return None
