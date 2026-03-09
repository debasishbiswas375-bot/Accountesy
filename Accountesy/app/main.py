import sys
import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Path injection for Render environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from routers import auth, converter, admin, dashboard

app = FastAPI(title="Accountesy")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Routes
app.include_router(dashboard.router)
app.include_router(auth.router)
app.include_router(converter.router)
app.include_router(admin.router) # Restricted to /admin

@app.get("/")
async def public_landing(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})
