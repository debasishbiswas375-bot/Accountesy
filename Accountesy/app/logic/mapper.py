# mapper.py - The Static AI Knowledge Base

# Major Search Keywords for Auto-Classification
ACCOUNTING_RULES = {
    "INDIRECT_EXPENSES": ["CHRG", "CHARGE", "FEE", "MAINTENANCE", "SMS", "ANNUAL", "RENEWAL", "FEE"],
    "DUTIES_AND_TAXES": ["GST", "TAX", "CGST", "SGST", "IGST", "VAT", "TDS", "INCOME TAX"],
    "CONTRA_CASH": ["CASH", "ATM", "SELF", "WITHDRAWAL", "DEPOSIT"],
    "ROUND_OFF": ["ROUND", "OFF", "DIFF"]
}

# Mapping for Tally XML Auto-Creation
GROUP_MAPPINGS = {
    "Bank Charges": "Indirect Expenses",
    "GST/Taxes": "Duties & Taxes",
    "Cash": "Cash-in-Hand",
    "Round Off": "Indirect Expenses",
    "Suspense A/c": "Suspense Account"
}

def auto_ai_search(narration):
    """
    Analyzes narration to find the best accounting category.
    Returns: (Ledger Name, Confidence Level)
    Confidence: 1 = Rule-Match, 0 = Unknown/Suspense
    """
    narr = narration.upper()
    
    if any(k in narr for k in ACCOUNTING_RULES["INDIRECT_EXPENSES"]):
        return "Bank Charges", 1
    
    if any(k in narr for k in ACCOUNTING_RULES["DUTIES_AND_TAXES"]):
        return "GST/Taxes", 1
        
    if any(k in narr for k in ACCOUNTING_RULES["CONTRA_CASH"]):
        return "Cash", 1
        
    return "Suspense A/c", 0
