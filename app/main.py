from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from fastapi.responses import HTMLResponse

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("landing.html", {
        "request": request
    })
# Routers
from app.routers.auth_routes import router as auth_router
from app.routers.workspace_routes import router as workspace_router
from app.routers.history_routes import router as history_router
from app.routers.admin_routes import router as admin_router
from app.routers.free_excel import router as free_excel_router

app = FastAPI()

# Static & Templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Routes
app.include_router(auth_router)
app.include_router(workspace_router)
app.include_router(history_router)
app.include_router(admin_router)
app.include_router(free_excel_router)
