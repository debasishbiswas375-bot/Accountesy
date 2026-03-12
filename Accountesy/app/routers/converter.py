import io, re, json, os, gzip, pandas as pd, pdfplumber
from bs4 import BeautifulSoup
from logic.mapper import auto_ai_search, GROUP_MAPPINGS

def calculate_credits(voucher_count):
    """0.1 credits per voucher - exactly as we planned."""
    return round(voucher_count * 0.1, 2)

async def get_preview_data(bank_file, master_file=None):
    # (Existing logic to extract data from PDF/Excel)
    # This remains the same as our previous 'processor.py' code
    # ensuring the AI suggests ledgers for the workspace table.
    pass

def generate_tally_xml(transactions, bank_name):
    """Generates XML and compresses it to save Supabase storage."""
    total_vch = len(transactions)
    credit_cost = calculate_credits(total_vch)
    
    # ... (XML Generation Logic) ...
    xml_content = "<ENVELOPE>...</ENVELOPE>" # Full XML string here
    
    # COMPRESSION SAFEGUARD
    compressed = gzip.compress(xml_content.encode('utf-8'))
    
    return xml_content, credit_cost, compressed
