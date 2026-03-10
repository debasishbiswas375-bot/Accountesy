import io, re, pandas as pd, pdfplumber
from bs4 import BeautifulSoup

async def get_preview_data(bank_file, master_file):
    # 1. Parse Ledgers from Master.html
    master_content = await master_file.read()
    soup = BeautifulSoup(master_content, "html.parser")
    tally_ledgers = [td.get_text().strip() for td in soup.find_all('td') if 'italic' in str(td.get('style'))]

    # 2. Extract PDF Data
    bank_content = await bank_file.read()
    all_rows = []
    with pdfplumber.open(io.BytesIO(bank_content)) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            if table: all_rows.extend(table)
    
    # 3. Dynamic Header Detection (Fixes missing Voucher Dates)
    header_idx = next((i for i, r in enumerate(all_rows) if any('date' in str(c).lower() for c in r if c)), 0)
    df = pd.DataFrame(all_rows[header_idx+1:], columns=all_rows[header_idx])
    date_col = next((c for c in df.columns if 'date' in str(c).lower()), df.columns[0])

    preview_results = []
    for _, row in df.iterrows():
        raw_date = str(row[date_col]).strip()
        if not re.search(r'\d', raw_date) or 'date' in raw_date.lower(): continue

        narr = str(row.get('Narration', row.get('Description', ''))).replace('\n', ' ').upper()
        debit = re.sub(r'[^\d.]', '', str(row.get('Debit', row.get('Withdrawal', '0')))) or "0"
        credit = re.sub(r'[^\d.]', '', str(row.get('Credit', row.get('Deposit', '0')))) or "0"

        # 4. AI Mapping & Suspense Tagging
        suggestions = [l for l in tally_ledgers if l.upper() in narr or l.upper()[:4] in narr]
        is_suspense = len(suggestions) != 1
        
        preview_results.append({
            "date": raw_date,
            "narration": f"{narr} [Suspense]" if is_suspense else narr,
            "amount": debit if float(debit) > 0 else credit,
            "type": "Payment" if float(debit) > 0 else "Receipt",
            "ledger": suggestions[0] if len(suggestions) == 1 else "Suspense A/c",
            "options": list(set(suggestions + ["Suspense A/c"]))[:4],
            "is_suspense": is_suspense
        })
    return preview_results, tally_ledgers

# --- THE MISSING FUNCTION CAUSING THE ERROR ---
def generate_tally_xml(transactions):
    xml = '<ENVELOPE><HEADER><TALLYREQUEST>Import Data</TALLYREQUEST></HEADER><BODY><IMPORTDATA><REQUESTDESC><REPORTNAME>Vouchers</REPORTNAME></REQUESTDESC><REQUESTDATA>'
    for tx in transactions:
        # Format date to YYYYMMDD for Tally
        clean_date = re.sub(r'\D', '', tx['date'])
        if len(clean_date) == 8: # DDMMYYYY -> YYYYMMDD
            clean_date = clean_date[4:] + clean_date[2:4] + clean_date[:2]
            
        xml += f"""
        <TALLYMESSAGE xmlns:UDF="TallyUDF">
            <VOUCHER VCHTYPE="{tx['type']}" ACTION="Create">
                <DATE>{clean_date}</DATE>
                <NARRATION>{tx['narration']}</NARRATION>
                <ALLLEDGERENTRIES.LIST>
                    <LEDGERNAME>{tx['ledger']}</LEDGERNAME>
                    <ISDEEMEDPOSITIVE>{"Yes" if tx['type'] == 'Payment' else "No"}</ISDEEMEDPOSITIVE>
                    <AMOUNT>{("-" if tx['type'] == 'Payment' else "") + tx['amount']}</AMOUNT>
                </ALLLEDGERENTRIES.LIST>
                <ALLLEDGERENTRIES.LIST>
                    <LEDGERNAME>State Bank of India-37017480905</LEDGERNAME>
                    <ISDEEMEDPOSITIVE>{"No" if tx['type'] == 'Payment' else "Yes"}</ISDEEMEDPOSITIVE>
                    <AMOUNT>{"-" if tx['type'] == 'Receipt' else ""}{tx['amount']}</AMOUNT>
                </ALLLEDGERENTRIES.LIST>
            </VOUCHER>
        </TALLYMESSAGE>"""
    return xml + '</REQUESTDATA></IMPORTDATA></BODY></ENVELOPE>'
