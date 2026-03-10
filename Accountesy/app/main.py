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

# --- ROOT PATH SETUP ---
app_dir = os.path.dirname(os.path.abspath(__file__)) 
root_dir = os.path.dirname(app_dir) 
sys.path.append(app_dir)

app = FastAPI(title="Accountesy")

# --- STATIC & TEMPLATES ---
app.mount("/static", StaticFiles(directory=os.path.join(root_dir, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(root_dir, "templates"))

# --- UNIVERSAL MAPPING ENGINE ---
def universal_bank_parser(content, filename):
    """Detects headers for any Indian Bank Statement autonomously."""
    if filename.endswith('.pdf'):
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            all_rows = []
            for page in pdf.pages:
                table = page.extract_table()
                if table: all_rows.extend(table)
            # Find the header row by looking for 'Date'
            header_idx = 0
            for i, row in enumerate(all_rows):
                if any('date' in str(cell).lower() for cell in row if cell):
                    header_idx = i
                    break
            df = pd.DataFrame(all_rows[header_idx+1:], columns=all_rows[header_idx])
    else:
        df = pd.read_excel(io.BytesIO(content), engine='openpyxl')

    # Clean headers: remove spaces and normalize for XML tags
    df.columns = [str(c).strip().replace(' ', '_').replace('.', '') for c in df.columns]
    
    # Universal Header Mapping Logic
    mapping = {}
    for col in df.columns:
        c_low = col.lower()
        if any(k in c_low for k in ['date', 'txn_dt']): mapping[col] = 'Date'
        elif any(k in c_low for k in ['desc', 'narr', 'partic']): mapping[col] = 'Narration'
        elif any(k in c_low for k in ['debit', 'withdr', 'dr']): mapping[col] = 'Debit'
        elif any(k in c_low for k in ['credit', 'depo', 'cr']): mapping[col] = 'Credit'
    
    return df.rename(columns=mapping)

# --- ROUTES ---
@app.get("/")
async def landing(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})

@app.get("/workspace")
async def workspace(request: Request):
    return templates.TemplateResponse("workspace.html", {"request": request})

@app.get("/history")
async def history(request: Request):
    return templates.TemplateResponse("history.html", {"request": request})

@app.get("/account")
async def account(request: Request):
    return templates.TemplateResponse("account.html", {"request": request})

@app.post("/convert/process")
async def process_conversion(bank_file: UploadFile = File(...), master_file: UploadFile = File(...)):
    try:
        # 1. Parse Tally Masters from Master.html (italic tags)
        master_content = await master_file.read()
        soup = BeautifulSoup(master_content, "html.parser")
        tally_ledgers = [td.get_text().strip() for td in soup.find_all('td') if 'italic' in str(td.get('style'))]

        # 2. Universal Parse Bank Statement
        bank_content = await bank_file.read()
        df = universal_bank_parser(bank_content, bank_file.filename.lower())

        # 3. AI Autonomous Ledger Mapping
        def match_ledger(narration):
            narration = str(narration).upper()
            # Priority matches for common narrations in your master
            if "PAYTM" in narration: return "PAYTM"
            if "HPCL" in narration: return "Hindustan Petroleum Corporation LTD"
            for ledger in tally_ledgers:
                if ledger.upper() in narration: return ledger
            return "Suspense A/c"

        if 'Narration' in df.columns:
            df['Suggested_Ledger'] = df['Narration'].apply(match_ledger)

        # 4. Generate Tally XML
        output = io.BytesIO()
        df.to_xml(output, index=False, root_name='ENVELOPE', row_name='VOUCHER')
        output.seek(0)

        return StreamingResponse(
            output, 
            media_type="application/xml",
            headers={"Content-Disposition": "attachment; filename=Accountesy_Universal_Tally.xml"}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Conversion Error: {str(e)}")
