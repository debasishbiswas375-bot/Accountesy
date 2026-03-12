import io, re, json, os, gzip, pandas as pd, pdfplumber
from bs4 import BeautifulSoup
from logic.mapper import auto_ai_search, GROUP_MAPPINGS

# AI Learning patterns are now stored in Supabase 'ai_memory' table
# But we keep a local cache for speed
MEMORY_FILE = os.path.join(os.path.dirname(__file__), "learning_db.json")

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f: return json.load(f)
    return {}

def save_pattern(narration, ledger):
    memory = load_memory()
    pattern = re.sub(r'\d+', '', narration).strip().upper()[:25]
    memory[pattern] = ledger
    with open(MEMORY_FILE, "w") as f: json.dump(memory, f)

async def get_preview_data(bank_file, master_file=None):
    memory = load_memory()
    tally_ledgers = list(GROUP_MAPPINGS.keys())
    if master_file:
        try:
            content = await master_file.read()
            soup = BeautifulSoup(content, "html.parser")
            custom = [td.get_text().strip() for td in soup.find_all('td') if 'italic' in str(td.get('style'))]
            tally_ledgers = list(set(tally_ledgers + custom))
        except: pass

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
    else:
        df = pd.read_excel(io.BytesIO(content))

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
        
        pattern = re.sub(r'\d+', '', narr).strip()[:20]
        if pattern in memory:
            tx_ledger, confidence = memory[pattern], 2
        else:
            tx_ledger, confidence = auto_ai_search(narr)
            if confidence == 0:
                matches = [l for l in tally_ledgers if l.upper() in narr or l.upper()[:5] in narr]
                if len(matches) == 1: tx_ledger, confidence = matches[0], 2

        results.append({
            "date": raw_date, "narration": narr, "amount": debit if is_pay else credit,
            "type": "Contra" if tx_ledger == "Cash" else ("Payment" if is_pay else "Receipt"),
            "ledger": tx_ledger, "confidence": confidence,
            "options": list(set([tx_ledger, "Bank Charges", "Cash", "Suspense A/c", "GST/Taxes"]))[:4]
        })
    results.sort(key=lambda x: x['confidence'])
    return results, tally_ledgers

def generate_tally_xml(transactions, bank_name):
    # --- PRICING LOGIC: 0.1 CREDITS PER VOUCHER ---
    total_vch = len(transactions)
    credit_cost = round(total_vch * 0.1, 2)
    
    xml = '<ENVELOPE><HEADER><TALLYREQUEST>Import Data</TALLYREQUEST></HEADER><BODY><IMPORTDATA><REQUESTDESC><REPORTNAME>Vouchers</REPORTNAME></REQUESTDESC><REQUESTDATA>'
    for led, grp in GROUP_MAPPINGS.items():
        xml += f'<TALLYMESSAGE><LEDGER NAME="{led}" ACTION="Create"><PARENT>{grp}</PARENT></LEDGER></TALLYMESSAGE>'

    for tx in transactions:
        d = re.sub(r'\D', '', tx['date'])[:8]
        if len(d) == 8 and not d.startswith(('20', '19')): d = d[4:] + d[2:4] + d[:2]
        xml += f'<TALLYMESSAGE><VOUCHER VCHTYPE="{tx["type"]}" ACTION="Create"><DATE>{d}</DATE><NARRATION>{tx["narration"]}</NARRATION><ALLLEDGERENTRIES.LIST><LEDGERNAME>{tx["ledger"]}</LEDGERNAME><ISDEEMEDPOSITIVE>{"Yes" if tx["type"]=="Payment" or (tx["type"]=="Contra" and tx["ledger"]=="Cash") else "No"}</ISDEEMEDPOSITIVE><AMOUNT>{("-" if tx["type"]=="Payment" or (tx["type"]=="Contra" and tx["ledger"]=="Cash") else "") + tx["amount"]}</AMOUNT></ALLLEDGERENTRIES.LIST><ALLLEDGERENTRIES.LIST><LEDGERNAME>{bank_name}</LEDGERNAME><ISDEEMEDPOSITIVE>{"No" if tx["type"]=="Payment" or (tx["type"]=="Contra" and tx["ledger"]=="Cash") else "Yes"}</ISDEEMEDPOSITIVE><AMOUNT>{"-" if tx["type"]=="Receipt" or (tx["type"]=="Contra" and tx["ledger"]!="Cash") else ""}{tx["amount"]}</AMOUNT></ALLLEDGERENTRIES.LIST></VOUCHER></TALLYMESSAGE>'
    
    final_xml = xml + '</REQUESTDATA></IMPORTDATA></BODY></ENVELOPE>'
    
    # --- STORAGE SAFEGUARD: COMPRESSION ---
    compressed = gzip.compress(final_xml.encode('utf-8'))
    return final_xml, credit_cost, compressed
