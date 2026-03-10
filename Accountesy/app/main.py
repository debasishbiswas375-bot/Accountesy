import sys
import os
from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# 1. PATH FIX: Find the 'Accountesy' folder (one level up from this file)
current_file_path = os.path.abspath(__file__) # Accountesy/app/main.py
app_dir = os.path.dirname(current_file_path) # Accountesy/app
accountesy_root = os.path.dirname(app_dir)   # Accountesy

# Add paths to system so routers/logic can be found
sys.path.append(app_dir)

from bs4 import BeautifulSoup
import pandas as pd
import io

# 2. DYNAMIC FOLDER DETECTION
# These point to Accountesy/static and Accountesy/templates
static_path = os.path.join(accountesy_root, "static")
template_path = os.path.join(accountesy_root, "templates")

# Fallback: If they aren't there, check inside the 'app' folder
if not os.path.exists(static_path):
    static_path = os.path.join(app_dir, "static")
if not os.path.exists(template_path):
    template_path = os.path.join(app_dir, "templates")

app = FastAPI(title="Accountesy")

# 3. MOUNT WITH VERIFIED PATHS
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")

templates = Jinja2Templates(directory=template_path)

# Register routers
try:
    from routers import auth, converter, dashboard
    app.include_router(dashboard.router)
    app.include_router(auth.router)
except ImportError as e:
    print(f"Router Import Warning: {e}")

# --- ROUTES ---
@app.get("/")
async def landing(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})

@app.get("/workspace")
async def workspace(request: Request):
    return templates.TemplateResponse("workspace.html", {"request": request})

@app.post("/convert/process")
async def process_conversion(bank_file: UploadFile = File(...), master_file: UploadFile = File(...)):
    try:
        master_content = await master_file.read()
        soup = BeautifulSoup(master_content, "html.parser")
        tally_ledgers = [td.get_text().strip() for td in soup.find_all('td') if td.get_text().strip()]
        return {"status": "Success", "ledgers_found": len(tally_ledgers)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
