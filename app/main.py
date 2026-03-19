from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Routers
from app.routers import workspace_routes, history_routes, free_excel, auth_routes, admin_routes

app = FastAPI()

# Static
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")

# Include routers (API + some pages)
app.include_router(workspace_routes.router)
app.include_router(history_routes.router)
app.include_router(free_excel.router)
app.include_router(auth_routes.router)
app.include_router(admin_routes.router)

# =========================
# ALL PAGE ROUTES (FULL)
# =========================

@app.get("/", response_class=HTMLResponse)
def landing(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})

@app.get("/workspace", response_class=HTMLResponse)
def workspace(request: Request):
    return templates.TemplateResponse("workspace.html", {"request": request})

@app.get("/workspace-preview", response_class=HTMLResponse)
def workspace_preview(request: Request):
    return templates.TemplateResponse("workspace_preview.html", {"request": request})

@app.get("/history", response_class=HTMLResponse)
def history(request: Request):
    return templates.TemplateResponse("history.html", {"request": request})

@app.get("/excel", response_class=HTMLResponse)
def excel(request: Request):
    return templates.TemplateResponse("excel.html", {"request": request})

@app.get("/help", response_class=HTMLResponse)
def help_page(request: Request):
    return templates.TemplateResponse("help.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
def login(request: Request):
    return templates.TemplateResponse("auth.html", {"request": request})
