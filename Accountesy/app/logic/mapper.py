import pandas as pd
from rapidfuzz import process, utils

def intelligent_header_mapping(df: pd.DataFrame):
    """
    AI-powered column detection. 
    Identifies Date, Narration, and Amount columns regardless of the bank's format.
    """
    # Clean column names
    df.columns = [str(c).strip().upper() for c in df.columns]
    
    mapping = {}
    
    # Keyword search for core accounting fields
    for col in df.columns:
        if any(k in col for k in ['DATE', 'VAL DT', 'TRANSACTION DATE']):
            mapping['Date'] = col
        if any(k in col for k in ['PARTICULARS', 'NARRATION', 'DESCRIPTION', 'REMARKS']):
            mapping['Narration'] = col
        if any(k in col for k in ['DEBIT', 'WITHDRAWAL', 'DR']):
            mapping['Debit'] = col
        if any(k in col for k in ['CREDIT', 'DEPOSIT', 'CR']):
            mapping['Credit'] = col
            
    # Rename columns to standard format for the Tally XML generator
    if mapping:
        df = df.rename(columns={v: k for k, v in mapping.items()})
        
    return df,
        
