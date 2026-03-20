import re

def find_best_ledger(narration, ledgers):
    narration = narration.lower()

    best = None
    best_score = 0

    for ledger in ledgers:
        l = ledger.lower()
        score = 0

        if l in narration:
            score += 80

        for word in l.split():
            if word in narration:
                score += 10

        if score > best_score:
            best_score = score
            best = ledger

    return best, best_score


def detect_bank_ledger(full_text, ledgers):
    match = re.search(r'Account Number\s*:\s*(\d+)', full_text)

    if not match:
        return None

    acc = match.group(1)[-5:]

    for ledger in ledgers:
        if acc in ledger:
            return ledger

    return None