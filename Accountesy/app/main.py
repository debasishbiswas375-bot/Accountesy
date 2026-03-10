import sys
import os
from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from bs4 import BeautifulSoup
import pandas as pd
import io

# CRITICAL: Path injection ensures all modules in the Accountesy folder are discoverable
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Now we can safely import your sub-routers and logic
from routers import auth, converter, admin, dashboard
from logic.mapper import intelligent_header_mapping

app = FastAPI(title="Accountesy")

# Configure static assets (logos) and frontend templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Register core application routers
app.include_router(dashboard.router)
app.include_router(auth.router)
app.include_router(converter.router)
app.include_router(admin.router)

# --- CORE PAGE ROUTES ---

@app.get("/")
async def public_landing(request: Request):
    """Serves the main landing page with your Debasish Biswas footer."""
    return templates.TemplateResponse("landing.html", {"request": request})

@app.get("/workspace")
async def workspace(request: Request):
    """Main AI Learning Workspace for Statement Conversion."""
    return templates.TemplateResponse("workspace.html", {"request": request})

@app.get("/features")
async def features(request: Request):
    """Details about Auto Ledger and Tally XML compatibility."""
    return templates.TemplateResponse("features.html", {"request": request})

@app.get("/pricing")
async def pricing(request: Request):
    """Display subscription plans."""
    return templates.TemplateResponse("pricing.html", {"request": request})

@app.get("/history")
async def history(request: Request):
    """User conversion history log."""
    return templates.TemplateResponse("history.html", {"request": request})

@app.get("/account")
async def account(request: Request):
    """User profile and account settings."""
    return templates.TemplateResponse("account.html", {"request": request})

# --- AI & TALLY CONVERSION LOGIC ---

@app.post("/convert/process")
async def process_conversion(
    request: Request, 
    bank_file: UploadFile = File(...), 
    master_file: UploadFile = File(...)
):
    """
    Handles real-world conversion by parsing master.html for Tally ledgers 
    and applying autonomous mapping to the bank statement.
    """
    try:
        # 1. Parse Tally master.html for ledger names
        master_content = await master_file.read()
        soup = BeautifulSoup(master_content, "html.parser")
        # Extracting all text from table cells (td) as potential ledger names
        tally_ledgers = list(set([td.get_text().strip() for td in soup.find_all('td') if td.get_text().strip()]))

        # 2. Read Bank Statement (Excel/CSV support)
        bank_content = await bank_file.read()
        df = pd.read_excel(io.BytesIO(bank_content))

        # 3. Apply AI Autonomous Mapping Logic
        df = intelligent_header_mapping(df)
        
        # Placeholder for AI learning: In a full build, tally_ledgers would 
        # be used here to match narrations to actual ledger names.
        
        return {"status": "success", "ledgers_found": len(tally_ledgers), "rows_processed": len(df)}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Conversion Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
