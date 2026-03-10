import sys
import os
from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# --- 1. SMART PATH INJECTION ---
# Adds the current folder to the path so 'routers' can be found easily
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from bs4 import BeautifulSoup
import pandas as pd
import io

# Import routers simply
try:
    from routers import auth, converter, admin, dashboard
except ImportError:
    # This handles different Render startup locations
    sys.path.append(os.path.join(current_dir, ".."))
    from routers import auth, converter, admin, dashboard

app = FastAPI(title="Accountesy")

# Setup paths for templates and static files
template_path = os.path.join(current_dir, "templates")
static_path = os.path.join(current_dir, "static")

app.mount("/static", StaticFiles(directory=static_path), name="static")
templates = Jinja2Templates(directory=template_path)

# Register routers
app.include_router(dashboard.router)
app.include_router(auth.router)

# --- ROUTES ---
@app.get("/")
async def public_landing(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})

@app.get("/workspace")
async def workspace(request: Request):
    return templates.TemplateResponse("workspace.html", {"request": request})

@app.get("/history")
async def history(request: Request):
    return templates.TemplateResponse("history.html", {"request": request})

@app.post("/convert/process")
async def process_conversion(bank_file: UploadFile = File(...), master_file: UploadFile = File(...)):
    try:
        master_content = await master_file.read()
        soup = BeautifulSoup(master_content, "html.parser")
        tally_ledgers = [td.get_text().strip() for td in soup.find_all('td') if td.get_text().strip()]
        return {"status": "Success", "ledgers_found": len(tally_ledgers)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
