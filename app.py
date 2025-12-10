import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from controllers.web import auth_web, advanced_report_web
from controllers.api.v1 import auth_api
from utils.logger import log_error
from starlette.exceptions import HTTPException as StarletteHTTPException

app = FastAPI(title="MyApp (MVC)")

BASE_DIR = os.path.dirname(__file__)
app.mount(
    "/static",
    StaticFiles(directory=os.path.join(BASE_DIR, "views", "static")),
    name="static",
)
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "views"))

app.include_router(auth_web.router)
app.include_router(advanced_report_web.router)

app.include_router(auth_api.router)

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return templates.TemplateResponse(
        "pages/errors/404.html",
        {"request": request},
        status_code=404
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    log_error(
        mensagem=f"Erro 500 não tratado: {str(exc)}",
        contexto="global_exception",
        dados_adicionais={"path": str(request.url), "traceback": str(exc)}
    )
    
    return templates.TemplateResponse(
        "pages/errors/500.html",
        {"request": request},
        status_code=500
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc):
    if exc.status_code == 404:
        return await not_found_handler(request, exc)

    return templates.TemplateResponse(
        "pages/errors/404.html",
        {"request": request},
        status_code=exc.status_code
    )