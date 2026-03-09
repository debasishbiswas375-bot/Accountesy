from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import Response
import pandas as pd
import pdfplumber
import io
import math
from app.database import get_db
from app.logic.mapper import intelligent_header_mapping

router = APIRouter(prefix="/convert", tags=["Converter"])

@router.post("/")
async def convert_statement(file: UploadFile = File(...)):
    filename = file.filename.lower()
    contents = await file.read()
    
    try:
        # 1. Load Data based on file type
        if filename.endswith('.pdf'):
            all_rows = []
            with pdfplumber.open(io.BytesIO(contents)) as pdf:
                for page in pdf.pages:
                    table = page.extract_table()
                    if table:
                        all_rows.extend(table)
            df = pd.DataFrame(all_rows[1:], columns=all_rows[0])
        elif filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        else:
            df = pd.read_excel(io.BytesIO(contents))

        # 2. Use the NEW Intelligent Mapper (No bank name needed!)
        df = intelligent_header_mapping(df)

        # 3. Credit Calculation (0.1 per voucher)
        # We count rows where either Debit or Credit has a value
        valid_rows = df[(df['Debit'].fillna(0) != 0) | (df['Credit'].fillna(0) != 0)]
        voucher_count = len(valid_rows)
        credits_needed = round(voucher_count * 0.1, 2)

        # Logic to check database balance would go here
        # For now, we process and return the XML
        
        # (XML Generation Logic remains the same...)
        return {"status": "success", "vouchers_found": voucher_count, "credits_deducted": credits_needed}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
