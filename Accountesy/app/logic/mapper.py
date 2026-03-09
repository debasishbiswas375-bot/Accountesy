import pandas as pd

def intelligent_header_mapping(df):
    mapping = {
        'Date': ['date', 'txn date', 'transaction date', 'vch date', 'value date'],
        'Narration': ['particulars', 'narration', 'description', 'remarks', 'chq/ref no'],
        'Debit': ['withdrawal', 'dr', 'debit', 'amount (dr)', 'payment'],
        'Credit': ['deposit', 'cr', 'credit', 'amount (cr)', 'receipt']
    }
    
    new_columns = {}
    for col in df.columns:
        clean_col = str(col).strip().lower()
        for standard, variations in mapping.items():
            if any(v in clean_col for v in variations):
                new_columns[col] = standard
    
    return df.rename(columns=new_columns)
