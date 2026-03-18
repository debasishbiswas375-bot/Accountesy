from flask import Blueprint, render_template, request, send_file, session
import os
import pandas as pd

# ENGINE
from tools.pdf_to_excel_engine import process_pdf_to_excel

workspace_bp = Blueprint('workspace', __name__)

UPLOAD_FOLDER = "uploads"

# Create upload folder if not exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


# =========================================
# 🏠 MAIN WORKSPACE PAGE (UNCHANGED)
# =========================================
@workspace_bp.route("/workspace")
def workspace_page():
    return render_template("workspace.html")


# =========================================
# 🔹 PDF → EXCEL
# =========================================
@workspace_bp.route("/convert-excel", methods=["POST"])
def convert_excel():
    file = request.files.get("file")

    if not file:
        return "❌ No file uploaded"

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    try:
        output_file = process_pdf_to_excel(file_path)

        return send_file(
            output_file,
            as_attachment=True,
            download_name=os.path.basename(output_file)
        )

    except Exception as e:
        return f"❌ Excel Error: {str(e)}"


# =========================================
# 🔹 XML GENERATOR FUNCTION
# =========================================
def generate_xml(df, output_path):
    xml = """<?xml version="1.0"?>
<ENVELOPE>
<HEADER><TALLYREQUEST>Import Data</TALLYREQUEST></HEADER>
<BODY><IMPORTDATA><REQUESTDESC><REPORTNAME>Vouchers</REPORTNAME></REQUESTDESC><REQUESTDATA>
"""

    for _, row in df.iterrows():
        credit = str(row.get("Credit", "")).strip()
        debit = str(row.get("Debit", "")).strip()

        if credit and credit != "nan":
            amount = credit
            vtype = "Receipt"
        else:
            amount = debit
            vtype = "Payment"

        xml += f"""
<TALLYMESSAGE>
<VOUCHER VCHTYPE="{vtype}" ACTION="Create">
<DATE>{row['Date'].replace('/', '')}</DATE>
<NARRATION>{row['Description']}</NARRATION>

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


# =========================================
# 🔹 PDF → XML
# =========================================
@workspace_bp.route("/convert-xml", methods=["POST"])
def convert_xml():
    file = request.files.get("file")

    if not file:
        return "❌ No file uploaded"

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    try:
        # Step 1 → Convert to Excel
        excel_file = process_pdf_to_excel(file_path)

        # Step 2 → Read Excel
        df = pd.read_excel(excel_file)

        # Step 3 → Generate XML
        output_xml = file_path.replace(".pdf", ".xml")
        generate_xml(df, output_xml)

        return send_file(
            output_xml,
            as_attachment=True,
            download_name=os.path.basename(output_xml)
        )

    except Exception as e:
        return f"❌ XML Error: {str(e)}"
