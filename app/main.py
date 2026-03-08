from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.routers import auth_routes, workspace_routes, history_routes, admin_routes

app = FastAPI(title="Accountesy – Accounting Expert")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

app.include_router(auth_routes.router)
app.include_router(workspace_routes.router)
app.include_router(history_routes.router)
app.include_router(admin_routes.router)

@app.get("/")
def landing(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})
