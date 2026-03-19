from fastapi import APIRouter, UploadFile, File
from fastapi.responses import FileResponse
import os
import pandas as pd

from app.tools.engine import process_pdf_to_excel

router = APIRouter()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# =========================================
# 🔹 PDF → EXCEL (PRO)
# =========================================
@router.post("/workspace/convert-excel")
async def convert_excel(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    try:
        output_file = process_pdf_to_excel(file_path)

        return FileResponse(
            output_file,
            filename=os.path.basename(output_file)
        )

    except Exception as e:
        return {"error": str(e)}


# =========================================
# 🔹 PDF → XML
# =========================================
def generate_xml(df, output_path):
    xml = """<?xml version="1.0"?>
<ENVELOPE>
<HEADER><TALLYREQUEST>Import Data</TALLYREQUEST></HEADER>
<BODY><IMPORTDATA><REQUESTDESC><REPORTNAME>Vouchers</REPORTNAME></REQUESTDESC><REQUESTDATA>
"""

    for _, row in df.iterrows():
        credit = str(row.get("credit", "")).strip()
        debit = str(row.get("debit", "")).strip()

        if credit and credit != "nan":
            amount = credit
            vtype = "Receipt"
        else:
            amount = debit
            vtype = "Payment"

        xml += f"""
<TALLYMESSAGE>
<VOUCHER VCHTYPE="{vtype}" ACTION="Create">
<DATE>{str(row.get('date','')).replace('/', '')}</DATE>
<NARRATION>{row.get('description','')}</NARRATION>

<ALLLEDGERENTRIES.LIST>
<LEDGERNAME>Bank Account</LEDGERNAME>
<ISDEEMEDPOSITIVE>{"Yes" if vtype=="Receipt" else "No"}</ISDEEMEDPOSITIVE>
<AMOUNT>{amount}</AMOUNT>
</ALLLEDGERENTRIES.LIST>

<ALLLEDGERENTRIES.LIST>
<LEDGERNAME>Suspense</LEDGERNAME>
<ISDEEMEDPOSITIVE>{"No" if vtype=="Receipt" else "Yes"}</ISDEEMEDPOSITIVE>
<AMOUNT>-{amount}</AMOUNT>
</ALLLEDGERENTRIES.LIST>

</VOUCHER>
</TALLYMESSAGE>
"""

    xml += "</REQUESTDATA></IMPORTDATA></BODY></ENVELOPE>"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(xml)

    return output_path


@router.post("/workspace/convert-xml")
async def convert_xml(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    try:
        excel_file = process_pdf_to_excel(file_path)
        df = pd.read_excel(excel_file)

        output_xml = file_path.replace(".pdf", ".xml")
        generate_xml(df, output_xml)

        return FileResponse(output_xml, filename=os.path.basename(output_xml))

    except Exception as e:
        return {"error": str(e)}
