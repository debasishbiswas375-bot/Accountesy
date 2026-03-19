import pandas as pd
import io

BANK_MAPS = {
    "date": ["date", "transaction date", "txn date", "value date", "date of transaction"],
    "description": ["description", "narration", "transaction remarks", "particulars", "remarks"],
    "amount": ["amount", "transaction amount", "withdrawals/deposits", "debit/credit", "txn amt"],
}

def smart_map_bank(file_bytes: bytes, filename: str):
    """Detects bank headers and standardizes columns."""
    if filename.endswith('.csv'):
        df = pd.read_csv(io.BytesIO(file_bytes))
    else:
        df = pd.read_excel(io.BytesIO(file_bytes))

    df.columns = [str(c).strip().lower() for c in df.columns]
    new_cols = {}
    
    for standard, variations in BANK_MAPS.items():
        for col in df.columns:
            if col in variations:
                new_cols[col] = standard
    
    df = df.rename(columns=new_cols)
    # Ensure mandatory columns exist
    for col in ["date", "description", "amount"]:
        if col not in df.columns:
            df[col] = "" 
    return df
