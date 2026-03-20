import re
from difflib import SequenceMatcher


# ==========================
# CLEAN
# ==========================
def clean(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9 ]', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()


def sim(a, b):
    return SequenceMatcher(None, a, b).ratio()


# ==========================
# 🔥 BANK DETECTION
# ==========================
def detect_bank_ledger(ledgers, full_text):
    match = re.search(r'account number\s*[:\-]?\s*(\d+)', full_text.lower())

    if match:
        last_digits = match.group(1)[-5:]

        for ledger in ledgers:
            if last_digits in ledger:
                return ledger

    for ledger in ledgers:
        if "bank" in ledger.lower():
            return ledger

    return "Bank Account"


# ==========================
# 🔥 PARTY NAME EXTRACTION
# ==========================
def extract_party(narration):
    narration = clean(narration)

    # common patterns
    patterns = [
        r'transfer to ([a-z ]+)',
        r'transfer from ([a-z ]+)',
        r'neft.* ([a-z ]+)',
        r'rtgs.* ([a-z ]+)',
        r'imps.* ([a-z ]+)'
    ]

    for p in patterns:
        match = re.search(p, narration)
        if match:
            return match.group(1).strip()

    return narration


# ==========================
# 🔥 AI MATCH (SMART)
# ==========================
def smart_match(narration, ledgers):
    narration_clean = clean(narration)

    party = extract_party(narration_clean)

    best = None
    best_score = 0

    for ledger in ledgers:
        ledger_clean = clean(ledger)

        score = 0

        # direct similarity
        score += sim(narration_clean, ledger_clean)

        # party matching boost
        if party in ledger_clean:
            score += 0.5

        # word match boost
        for w in ledger_clean.split():
            if w in narration_clean:
                score += 0.1

        if score > best_score:
            best_score = score
            best = ledger

    confidence = min(best_score, 0.95)

    if best:
        return best, confidence

    return "Suspense", 0.4


# ==========================
# 🔥 VOUCHER TYPE DETECTION
# ==========================
def detect_voucher(tx):
    narration = clean(tx["narration"])
    amount = tx["amount"]

    if amount > 0:
        if any(x in narration for x in ["neft", "rtgs", "imps", "transfer from"]):
            return "Receipt"

    if amount < 0:
        if any(x in narration for x in ["loan", "emi"]):
            return "Journal"
        if any(x in narration for x in ["salary"]):
            return "Payment"
        return "Payment"

    return "Journal"


# ==========================
# 🔥 MAIN ENGINE
# ==========================
def map_transactions(transactions, ledgers, full_text):
    mapped = []

    bank_ledger = detect_bank_ledger(ledgers, full_text)

    for tx in transactions:
        narration = tx["narration"]

        ledger, confidence = smart_match(narration, ledgers)
        voucher_type = detect_voucher(tx)

        if confidence >= 0.75:
            color = "green"
        elif confidence >= 0.6:
            color = "orange"
        else:
            color = "red"
            ledger = "Suspense"

        mapped.append({
            **tx,
            "ledger": ledger,
            "final_ledger": ledger,
            "confidence": round(confidence, 2),
            "color": color,
            "voucher_type": voucher_type,
            "bank": bank_ledger
        })

    return mapped