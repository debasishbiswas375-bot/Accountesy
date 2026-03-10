import io
import pandas as pd
import pdfplumber
from bs4 import BeautifulSoup
import re

async def process_tally_conversion(bank_file, master_file):
    # 1. Read Master.html Ledgers
    master_content = await master_file.read()
    soup = BeautifulSoup(master_content, "html.parser")
    ledgers = [td.get_text().strip() for td in soup.find_all('td') if 'italic' in str(td.get('style'))]

    # 2. Extract Bank Data (PDF or Excel)
    bank_content = await bank_file.read()
    if bank_file.filename.lower().endswith('.pdf'):
        with pdfplumber.open(io.BytesIO(bank_content)) as pdf:
            rows = []
            for page in pdf.pages:
                table = page.extract_table()
                if table: rows.extend(table)
            # FIX: Skip header rows by finding the first row starting with a Date
            clean_rows = [r for r in rows if r[0] and re.match(r'\d{2}/\d{2}/\d{4}', str(r[0]))]
            df = pd.DataFrame(clean_rows, columns=['Date', 'ValueDate', 'Narration', 'Ref', 'Branch', 'Debit', 'Credit', 'Balance'])
    else:
        df = pd.read_excel(io.BytesIO(bank_content), engine='openpyxl')

    # 3. Build Strict Tally XML (Double Entry Logic)
    xml = '<ENVELOPE><HEADER><TALLYREQUEST>Import Data</TALLYREQUEST></HEADER><BODY><IMPORTDATA><REQUESTDESC><REPORTNAME>Vouchers</REPORTNAME></REQUESTDESC><REQUESTDATA>'
    
    for _, row in df.iterrows():
        # Sanitize numbers to prevent string-to-float errors
        def to_num(val): return re.sub(r'[^\d.]', '', str(val)) or "0"
        
        dr, cr = to_num(row.get('Debit', 0)), to_num(row.get('Credit', 0))
        amt = dr if float(dr) > 0 else cr
        v_type = "Payment" if float(dr) > 0 else "Receipt"
        date = str(row['Date']).replace('/', '').split(' ')[0]

        # Smart Match
        target = next((l for l in ledgers if l.upper() in str(row['Narration']).upper()), "Suspenses")

        xml += f"""
        <TALLYMESSAGE xmlns:UDF="TallyUDF">
            <VOUCHER VCHTYPE="{v_type}" ACTION="Create">
                <DATE>{date}</DATE>
                <NARRATION>{row['Narration']}</NARRATION>
                <ALLLEDGERENTRIES.LIST>
                    <LEDGERNAME>{target}</LEDGERNAME>
                    <ISDEEMEDPOSITIVE>{"Yes" if v_type == "Payment" else "No"}</ISDEEMEDPOSITIVE>
                    <AMOUNT>{("-" if v_type == "Payment" else "") + amt}</AMOUNT>
                </ALLLEDGERENTRIES.LIST>
                <ALLLEDGERENTRIES.LIST>
                    <LEDGERNAME>State Bank of India-37017480905</LEDGERNAME>
                    <ISDEEMEDPOSITIVE>{"No" if v_type == "Payment" else "Yes"}</ISDEEMEDPOSITIVE>
                    <AMOUNT>{"-" if v_type == "Receipt" else ""}{amt}</AMOUNT>
                </ALLLEDGERENTRIES.LIST>
            </VOUCHER>
        </TALLYMESSAGE>"""

    return (xml + '</REQUESTDATA></IMPORTDATA></BODY></ENVELOPE>').encode('utf-8')
