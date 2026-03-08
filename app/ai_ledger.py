def detect_ledger(narration):
    narration = narration.lower()
    if "amazon" in narration:
        return "Purchase Account"
    if "salary" in narration:
        return "Salary Expense"
    if "upi" in narration:
        return "Bank Transfer"
    return "Suspense Ledger"
