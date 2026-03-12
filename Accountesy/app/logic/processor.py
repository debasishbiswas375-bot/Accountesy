import io, re, json, os, pandas as pd, pdfplumber
from bs4 import BeautifulSoup

MEMORY_FILE = os.path.join(os.path.dirname(__file__), "learning_db.json")

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f: return json.load(f)
    return {}

async def get_preview_data(bank_file, master_file=None):
    # 1. THE AI KNOWLEDGE BASE
    # Default Tally structures prioritized by accounting standards
    base_ledgers = {
        "Bank Charges": "Indirect Expenses",
        "Cash": "Cash-in-Hand",
        "Suspense A/c": "Suspense Account",
        "GST/Taxes": "Duties & Taxes",
        "Round Off": "Indirect Expenses"
    }
    
    memory = load_memory()
    tally_ledgers = list(base_ledgers.keys())
    
    if master_file:
        try:
            content = await master_file.read()
            soup = BeautifulSoup(content, "html.parser")
            custom = [td.get_text().strip() for td in soup.find_all('td') if 'italic' in str(td.get('style'))]
            tally_ledgers = list(set(tally_ledgers + custom))
        except: pass

    # 2. MULTI-FORMAT EXTRACTION ENGINE
    filename = bank_file.filename.lower()
    content = await bank_file.read()
    
    if filename.endswith('.pdf'):
        all_rows = []
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            for page in pdf.pages:
                table = page.extract_table()
                if table: all_rows.extend(table)
        header_idx = next((i for i, r in enumerate(all_rows) if any('date' in str(c).lower() for c in r if c)), 0)
        df = pd.DataFrame(all_rows[header_idx+1:], columns=all_rows[header_idx])
    elif filename.endswith(('.xlsx', '.xls')):
        df = pd.read_excel(io.BytesIO(content))
    else:
        df = pd.read_csv(io.BytesIO(content))

    # Clean Headers for Search Logic
    df.columns = [str(c).strip().lower() for c in df.columns]
    date_col = next((c for c in df.columns if 'date' in c), df.columns[0])
    narr_col = next((c for c in df.columns if any(k in c for k in ['narr', 'desc', 'partic'])), None)
    debit_col = next((c for c in df.columns if any(k in c for k in ['debit', 'withdraw'])), None)
    credit_col = next((c for c in df.columns if any(k in c for k in ['credit', 'deposit'])), None)

    results = []
    for _, row in df.iterrows():
        raw_date = str(row[date_col]).strip()
        if not re.search(r'\d', raw_date) or 'nan' in raw_date.lower(): continue

        narr = str(row.get(narr_col, '')).upper()
        debit = re.sub(r'[^\d.]', '', str(row.get(debit_col, '0'))) or "0"
        credit = re.sub(r'[^\d.]', '', str(row.get(credit_col, '0'))) or "0"
        is_pay = float(debit) > 0
        amt = debit if is_pay else credit

        # --- 3. AUTO-AI SEARCH & SORT HIERARCHY ---
        tx_ledger = "Suspense A/c"
        confidence_score = 0 # 0=Low (Red), 1=Rule-Based (Yellow), 2=Learned (Green)
        
        # Level 1: Search Learned Memory (High Confidence)
        pattern = re.sub(r'\d+', '', narr).strip()[:20]
        if pattern in memory:
            tx_ledger, confidence_score = memory[pattern], 2
            
        # Level 2: Rule-Based Search (AI Logic)
        elif any(k in narr for k in ["CHRG", "FEE", "MAINTENANCE"]):
            tx_ledger, confidence_score = "Bank Charges", 1
        elif any(k in narr for k in ["GST", "TAX", "DUTY"]):
            tx_ledger, confidence_score = "GST/Taxes", 1
        elif any(k in narr for k in ["CASH", "ATM", "SELF"]):
            tx_ledger, confidence_score = "Cash", 1
            
        # Level 3: Fuzzy Master Matching
        else:
            matches = [l for l in tally_ledgers if l.upper() in narr or l.upper()[:5] in narr]
            if len(matches) == 1:
                tx_ledger, confidence_score = matches[0], 2
        
        # Determine Voucher Type
        if tx_ledger == "Cash": vch_type = "Contra"
        else: vch_type = "Payment" if is_pay else "Receipt"

        results.append({
            "date": raw_date,
            "narration": narr,
            "amount": amt,
            "type": vch_type,
            "ledger": tx_ledger,
            "confidence": confidence_score, # Used for sorting in frontend
            "options": list(set([tx_ledger, "Bank Charges", "Cash", "Suspense A/c"]))[:5]
        })

    # SORT: Move low confidence (Suspense) to the top so user sees them first
    results.sort(key=lambda x: x['confidence'])
    
    return results, tally_ledgers

def generate_tally_xml(transactions, bank_name="Bank Account"):
    """
    Final XML with Auto-Creation of Missing Ledgers
    """
    xml = '<ENVELOPE><HEADER><TALLYREQUEST>Import Data</TALLYREQUEST></HEADER><BODY><IMPORTDATA><REQUESTDESC><REPORTNAME>Vouchers</REPORTNAME></REQUESTDESC><REQUESTDATA>'
    
    # Auto-Create Group Mappings
    ledger_groups = {"Bank Charges": "Indirect Expenses", "GST/Taxes": "Duties & Taxes"}
    for led, grp in ledger_groups.items():
        xml += f'<TALLYMESSAGE xmlns:UDF="TallyUDF"><LEDGER NAME="{led}" ACTION="Create"><PARENT>{grp}</PARENT></LEDGER></TALLYMESSAGE>'

    for tx in transactions:
        # Standard Date formatting logic...
        clean_date = re.sub(r'\D', '', tx['date'])[:8]
        if len(clean_date) == 8 and not clean_date.startswith(('20', '19')):
            clean_date = clean_date[4:] + clean_date[2:4] + clean_date[:2]

        xml += f"""
        <TALLYMESSAGE xmlns:UDF="TallyUDF">
            <VOUCHER VCHTYPE="{tx['type']}" ACTION="Create">
                <DATE>{clean_date}</DATE>
                <NARRATION>{tx['narration']}</NARRATION>
                <ALLLEDGERENTRIES.LIST>
                    <LEDGERNAME>{tx['ledger']}</LEDGERNAME>
                    <ISDEEMEDPOSITIVE>{"Yes" if tx['type'] == 'Payment' or (tx['type'] == 'Contra' and tx['ledger'] == 'Cash') else "No"}</ISDEEMEDPOSITIVE>
                    <AMOUNT>{("-" if tx['type'] == 'Payment' or (tx['type'] == 'Contra' and tx['ledger'] == 'Cash') else "") + tx['amount']}</AMOUNT>
                </ALLLEDGERENTRIES.LIST>
                <ALLLEDGERENTRIES.LIST>
                    <LEDGERNAME>{bank_name}</LEDGERNAME>
                    <ISDEEMEDPOSITIVE>{"No" if tx['type'] == 'Payment' or (tx['type'] == 'Contra' and tx['ledger'] == 'Cash') else "Yes"}</ISDEEMEDPOSITIVE>
                    <AMOUNT>{"-" if tx['type'] == 'Receipt' or (tx['type'] == 'Contra' and tx['ledger'] != 'Cash') else ""}{tx['amount']}</AMOUNT>
                </ALLLEDGERENTRIES.LIST>
            </VOUCHER>
        </TALLYMESSAGE>"""
    return xml + '</REQUESTDATA></IMPORTDATA></BODY></ENVELOPE>'
