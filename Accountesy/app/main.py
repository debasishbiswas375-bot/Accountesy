import sys
import os
import io
import pandas as pd
from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from bs4 import BeautifulSoup

# CRITICAL: Ensures modules in the Accountesy folder are discoverable
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from routers import auth, converter, admin, dashboard

app = FastAPI(title="Accountesy")

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Register routers
app.include_router(dashboard.router)
app.include_router(auth.router)
app.include_router(converter.router)
app.include_router(admin.router)

# --- PAGE ROUTES (Fixed to prevent 404/500 errors) ---

@app.get("/")
async def public_landing(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})

@app.get("/workspace")
async def workspace(request: Request):
    return templates.TemplateResponse("workspace.html", {"request": request})

@app.get("/features")
async def features(request: Request):
    return templates.TemplateResponse("features.html", {"request": request})

@app.get("/pricing")
async def pricing(request: Request):
    return templates.TemplateResponse("pricing.html", {"request": request})

@app.get("/history")
async def history(request: Request):
    return templates.TemplateResponse("history.html", {"request": request})

@app.get("/account")
async def account(request: Request):
    return templates.TemplateResponse("account.html", {"request": request})

# --- THE CONVERSION TOOL ENGINE ---

@app.post("/convert/process")
async def process_conversion(bank_file: UploadFile = File(...), master_file: UploadFile = File(...)):
    """
    Handles real-world conversion by parsing master.html for Tally ledgers 
    and applying autonomous mapping to the bank statement.
    """
    try:
        # 1. Parse Tally master.html for your specific ledger names
        master_content = await master_file.read()
        soup = BeautifulSoup(master_content, "html.parser")
        tally_ledgers = [td.get_text().strip() for td in soup.find_all('td') if td.get_text().strip()]

        # 2. Read your Bank Statement (Excel/CSV)
        bank_content = await bank_file.read()
        df = pd.read_excel(io.BytesIO(bank_content))

        # 3. AI Autonomous Mapping (Placeholder logic)
        # Matches narrations against your actual Tally masters
        df['Suggested_Ledger'] = df.iloc[:, 1].apply(
            lambda x: next((l for l in tally_ledgers if l.lower() in str(x).lower()), "Suspense A/c")
        )

        return {
            "status": "Success",
            "message": f"AI identified {len(df)} transactions and matched them to your Tally masters.",
            "ledgers_found": len(tally_ledgers)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Conversion Error: {str(e)}")
