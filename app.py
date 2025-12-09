import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from controllers.web import auth_web, advanced_report_web
from controllers.api.v1 import auth_api

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
