from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import Response
import pandas as pd
import pdfplumber
import io
import math
from app.database import get_db

router = APIRouter(prefix="/convert", tags=["Converter"])

def format_tally_date(date_str):
    if pd.isna(date_str) or not str(date_str).strip():
        return ""
    try:
        d = pd.to_datetime(str(date_str), dayfirst=True)
        return d.strftime("%Y%m%d")
    except:
        return ""

def generate_tally_xml(df):
    xml_data = "<ENVELOPE>\n<HEADER>\n<TALLYREQUEST>Import Data</TALLYREQUEST>\n</HEADER>\n<BODY>\n<IMPORTDATA>\n<REQUESTDESC>\n<REPORTNAME>Vouchers</REPORTNAME>\n<STATICVARIABLES>\n<SVCURRENTCOMPANY>Company Name</SVCURRENTCOMPANY>\n</STATICVARIABLES>\n</REQUESTDESC>\n<REQUESTDATA>\n"
    
    for index, row in df.iterrows():
        date = format_tally_date(row.get('Date', ''))
        narration = str(row.get('Narration', 'Bank Transaction')).replace('&', '&amp;')
        
        debit = pd.to_numeric(str(row.get('Debit', '0')).replace(',', '').replace('₹', '').strip(), errors='coerce')
        credit = pd.to_numeric(str(row.get('Credit', '0')).replace(',', '').replace('₹', '').strip(), errors='coerce')
        
        if math.isnan(debit): debit = 0
        if math.isnan(credit): credit = 0
        
        if debit == 0 and credit == 0: continue

        xml_data += "<TALLYMESSAGE xmlns:UDF=\"TallyUDF\">\n"
        
        if debit > 0:
            vch_type = "Payment"
            ledger_1 = "Suspense"
            amount_1 = f"-{debit}"
            ledger_2 = "Bank Account"
            amount_2 = f"{debit}"
        else:
            vch_type = "Receipt"
            ledger_1 = "Bank Account"
            amount_1 = f"-{credit}"
            ledger_2 = "Suspense"
            amount_2 = f"{credit}"

        xml_data += f"<VOUCHER VCHTYPE=\"{vch_type}\" ACTION=\"Create\">\n<DATE>{date}</DATE>\n<VOUCHERTYPENAME>{vch_type}</VOUCHERTYPENAME>\n<NARRATION>{narration}</NARRATION>\n<ALLLEDGERENTRIES.LIST>\n<LEDGERNAME>{ledger_1}</LEDGERNAME>\n<ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE>\n<AMOUNT>{amount_1}</AMOUNT>\n</ALLLEDGERENTRIES.LIST>\n<ALLLEDGERENTRIES.LIST>\n<LEDGERNAME>{ledger_2}</LEDGERNAME>\n<ISDEEMEDPOSITIVE>No</ISDEEMEDPOSITIVE>\n<AMOUNT>{amount_2}</AMOUNT>\n</ALLLEDGERENTRIES.LIST>\n</VOUCHER>\n</TALLYMESSAGE>\n"

    xml_data += "</REQUESTDATA>\n</IMPORTDATA>\n</BODY>\n</ENVELOPE>"
    return xml_data

@router.post("/")
async def convert_statement(file: UploadFile = File(...)):
    filename = file.filename.lower()
    if not filename.endswith(('.xlsx', '.csv', '.pdf')):
        raise HTTPException(status_code=400, detail="Invalid file type.")

    try:
        contents = await file.read()
        
        if filename.endswith('.pdf'):
            all_rows = []
            with pdfplumber.open(io.BytesIO(contents)) as pdf:
                for page in pdf.pages:
                    table = page.extract_table()
                    if table:
                        cleaned_table = [row for row in table if any(cell for cell in row)]
                        all_rows.extend(cleaned_table)
            if not all_rows: raise HTTPException(status_code=400, detail="No data in PDF.")
            df = pd.DataFrame(all_rows[1:], columns=all_rows[0])
            
        elif filename.endswith('.csv'): df = pd.read_csv(io.BytesIO(contents))
        else: df = pd.read_excel(io.BytesIO(contents))
        
        df.columns = [str(col).strip().title() for col in df.columns]
        column_mapping = {
            'Withdrawal': 'Debit', 'Withdrawals': 'Debit', 'Dr Amount': 'Debit',
            'Deposit': 'Credit', 'Deposits': 'Credit', 'Cr Amount': 'Credit',
            'Remarks': 'Narration', 'Description': 'Narration', 'Particulars': 'Narration',
            'Txn Date': 'Date', 'Value Date': 'Date', 'Transaction Date': 'Date'
        }
        df.rename(columns=column_mapping, inplace=True)

        # --- NEW: CREDIT DEDUCTION LOGIC ---
        db = get_db()
        
        # 1. Calculate Valid Vouchers
        df['Debit'] = pd.to_numeric(df.get('Debit', 0), errors='coerce').fillna(0)
        df['Credit'] = pd.to_numeric(df.get('Credit', 0), errors='coerce').fillna(0)
        valid_vouchers = len(df[(df['Debit'] > 0) | (df['Credit'] > 0)])
        
        if valid_vouchers == 0:
            raise HTTPException(status_code=400, detail="No valid transactions found to convert.")
            
        # 2. Calculate Required Credits (0.1 per voucher)
        required_credits = valid_vouchers * 0.1
        
        # 3. MOCK USER ID (Replace 'USER_UUID_HERE' with real user ID from session later)
        mock_user_id = "USER_UUID_HERE" 
        
        ''' 
        # UNCOMMENT THIS WHEN AUTH IS FULLY CONNECTED
        user_response = db.table("users").select("credits").eq("id", mock_user_id).execute()
        current_credits = user_response.data[0]['credits']
        
        if current_credits < required_credits:
            raise HTTPException(status_code=402, detail=f"Insufficient balance. You need {required_credits} credits for {valid_vouchers} vouchers.")
            
        new_balance = current_credits - required_credits
        db.table("users").update({"credits": new_balance}).eq("id", mock_user_id).execute()
        
        # Log into conversion_history table
        db.table("conversion_history").insert({
            "user_id": mock_user_id,
            "file_name": file.filename,
            "credits_used": required_credits,
            "status": "Success"
        }).execute()
        '''

        # Generate XML Output
        tally_xml = generate_tally_xml(df)
        return Response(content=tally_xml, media_type="application/xml", headers={"Content-Disposition": f"attachment; filename=Accountesy_{file.filename}.xml"})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
