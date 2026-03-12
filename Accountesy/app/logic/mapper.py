# mapper.py - The Static AI Knowledge Base

ACCOUNTING_RULES = {
    "INDIRECT_EXPENSES": ["CHRG", "CHARGE", "FEE", "MAINTENANCE", "SMS", "ANNUAL", "RENEWAL"],
    "DUTIES_AND_TAXES": ["GST", "TAX", "CGST", "SGST", "IGST", "VAT", "TDS"],
    "CONTRA_CASH": ["CASH", "ATM", "SELF", "WITHDRAWAL", "DEPOSIT"]
}

# These map to standard Tally groups
GROUP_MAPPINGS = {
    "Bank Charges": "Indirect Expenses",
    "GST/Taxes": "Duties & Taxes",
    "Cash": "Cash-in-Hand",
    "Suspense A/c": "Suspense Account"
}

def auto_ai_search(narration):
    """Analyzes narration to find the best accounting category."""
    narr = narration.upper()
    if any(k in narr for k in ACCOUNTING_RULES["INDIRECT_EXPENSES"]):
        return "Bank Charges", 1
    if any(k in narr for k in ACCOUNTING_RULES["DUTIES_AND_TAXES"]):
        return "GST/Taxes", 1
    if any(k in narr for k in ACCOUNTING_RULES["CONTRA_CASH"]):
        return "Cash", 1
    return "Suspense A/c", 0
