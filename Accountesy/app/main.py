import sys
import os
import io
import pandas as pd
from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import StreamingResponse
from bs4 import BeautifulSoup

# --- ROOT PATH & DIRECTORY CONFIG ---
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
accountesy_root = os.path.dirname(current_dir)

app = FastAPI(title="Accountesy")

# Configure dynamic paths for Render
static_path = os.path.join(accountesy_root, "static")
template_path = os.path.join(accountesy_root, "templates")

app.mount("/static", StaticFiles(directory=static_path), name="static")
templates = Jinja2Templates(directory=template_path)

# --- PAGE ROUTES ---
@app.get("/")
async def landing(request: Request):
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

# --- CONVERSION TOOL ENGINE ---
@app.post("/convert/process")
async def process_conversion(bank_file: UploadFile = File(...), master_file: UploadFile = File(...)):
    try:
        master_content = await master_file.read()
        soup = BeautifulSoup(master_content, "html.parser")
        tally_ledgers = [td.get_text().strip() for td in soup.find_all('td') if td.get_text().strip()]

        bank_content = await bank_file.read()
        df = pd.read_excel(io.BytesIO(bank_content))
        
        # Suggested_Ledger Mapping
        df['Suggested_Ledger'] = df.iloc[:, 1].apply(
            lambda x: next((l for l in tally_ledgers if l.lower() in str(x).lower()), "Suspense A/c")
        )

        output = io.BytesIO()
        df.to_xml(output, index=False, root_name='TALLYMESSAGE', row_name='VOUCHER')
        output.seek(0)

        return StreamingResponse(
            output, 
            media_type="application/xml",
            headers={"Content-Disposition": "attachment; filename=Accountesy_Tally_Export.xml"}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
