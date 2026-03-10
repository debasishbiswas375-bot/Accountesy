import sys
import os
import io
import pandas as pd
import pdfplumber
from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import StreamingResponse
from bs4 import BeautifulSoup

# --- 1. ABSOLUTE PATH CALCULATION ---
# Ensures 'static' and 'templates' are found correctly on Render
app_dir = os.path.dirname(os.path.abspath(__file__)) 
root_dir = os.path.dirname(app_dir) 

app = FastAPI(title="Accountesy")

# --- 2. MOUNTING & TEMPLATES ---
app.mount("/static", StaticFiles(directory=os.path.join(root_dir, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(root_dir, "templates"))

# --- 3. PAGE ROUTES (Clean URLs for Sidebar) ---
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

# --- 4. THE CONVERSION ENGINE (Fixes Excel/PDF Errors) ---
@app.post("/convert/process")
async def process_conversion(bank_file: UploadFile = File(...), master_file: UploadFile = File(...)):
    try:
        # Parse Tally Masters
        master_content = await master_file.read()
        soup = BeautifulSoup(master_content, "html.parser")
        tally_ledgers = [td.get_text().strip() for td in soup.find_all('td') if td.get_text().strip()]

        # Read Bank Statement with Explicit Engine
        bank_content = await bank_file.read()
        filename = bank_file.filename.lower()

        if filename.endswith(('.xlsx', '.xls')):
            # Fixes: "Excel file format cannot be determined"
            df = pd.read_excel(io.BytesIO(bank_content), engine='openpyxl')
        elif filename.endswith('.pdf'):
            with pdfplumber.open(io.BytesIO(bank_content)) as pdf:
                data = [page.extract_table() for page in pdf.pages if page.extract_table()]
                df = pd.DataFrame(data[0][1:], columns=data[0][0])
        else:
            raise HTTPException(status_code=400, detail="Unsupported format. Use PDF or Excel.")

        # AI Mapping logic
        df['Suggested_Ledger'] = df.iloc[:, 1].apply(
            lambda x: next((l for l in tally_ledgers if l.lower() in str(x).lower()), "Suspense A/c")
        )

        output = io.BytesIO()
        df.to_xml(output, index=False, root_name='TALLYMESSAGE', row_name='VOUCHER')
        output.seek(0)

        return StreamingResponse(
            output, 
            media_type="application/xml",
            headers={"Content-Disposition": f"attachment; filename=Accountesy_Export.xml"}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
