import sys
import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Path injection ensures all modules in the Accountesy folder are discoverable
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from routers import auth, converter, admin, dashboard

app = FastAPI(title="Accountesy")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Register core routers
app.include_router(dashboard.router)
app.include_router(auth.router)
app.include_router(converter.router)
app.include_router(admin.router)

# Define the specific workspace and AI mapping pages
@app.get("/")
async def public_landing(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})

@app.get("/workspace")
async def workspace(request: Request):
    return templates.TemplateResponse("workspace.html", {"request": request})

@app.get("/pricing")
async def pricing(request: Request):
    return templates.TemplateResponse("pricing.html", {"request": request})

@app.get("/history")
async def history(request: Request):
    return templates.TemplateResponse("history.html", {"request": request})

@app.get("/features")
async def features(request: Request):
    return templates.TemplateResponse("features.html", {"request": request})

@app.get("/account")
async def account(request: Request):
    return templates.TemplateResponse("account.html", {"request": request})
