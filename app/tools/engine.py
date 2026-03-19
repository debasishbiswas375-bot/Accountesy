from app.database import supabase

def match_master(txn, master_ledgers):
    for ledger in master_ledgers:
        if ledger.lower() in txn["description"].lower():
            return ledger
    return None


def match_ai_memory(txn, user_id):
    res = supabase.table("ai_memory").select("*").eq("user_id", user_id).execute()
    for item in res.data:
        if item["narration_pattern"] in txn["description"].lower():
            return item["suggested_ledger"]
    return None


def rule_based(txn):
    desc = txn["description"].lower()

    if "gst" in desc:
        return "GST Expense"
    if "petrol" in desc:
        return "Fuel Expense"
    if "zomato" in desc:
        return "Staff Welfare"

    return None


def assign_ledger(txn, user_id, master_ledgers=None, user_default=None):
    ledger = None

    # MASTER
    if master_ledgers:
        ledger = match_master(txn, master_ledgers)

    # AI
    if not ledger:
        ledger = match_ai_memory(txn, user_id)

    # RULE
    if not ledger:
        ledger = rule_based(txn)

    # USER DEFAULT
    if not ledger and user_default:
        ledger = user_default

    # FALLBACK
    if not ledger:
        ledger = "Suspense Account"

    return ledger


# 🔥 LEARNING
def learn_pattern(user_id, narration, ledger):
    supabase.table("ai_memory").upsert({
        "user_id": user_id,
        "narration_pattern": narration.lower(),
        "suggested_ledger": ledger
    }, on_conflict="user_id,narration_pattern").execute()
