import re


# ==========================
# PARSE MASTER.HTML
# ==========================
def parse_master_html(master_bytes):
    if not master_bytes:
        return []

    html = master_bytes.decode("utf-8", errors="ignore")

    # Extract ledger names (basic)
    ledgers = re.findall(r"<LEDGER NAME=\"(.*?)\"", html)

    return [l.lower() for l in ledgers]


# ==========================
# LOAD USER LEARNINGS
# ==========================
def load_user_mappings(supabase, user_id):
    try:
        res = supabase.table("mappings") \
            .select("*") \
            .eq("user_id", user_id) \
            .execute()

        mappings = {}
        for row in res.data:
            mappings[row["keyword"]] = row["ledger_name"]

        return mappings

    except:
        return {}


# ==========================
# SAVE NEW LEARNING
# ==========================
def save_mapping(supabase, user_id, keyword, ledger):
    try:
        supabase.table("mappings").insert({
            "user_id": user_id,
            "keyword": keyword,
            "ledger_name": ledger
        }).execute()
    except:
        pass


# ==========================
# MATCH LEDGER
# ==========================
def match_ledger(narration, ledger_list, user_map):
    narration = narration.lower()

    # ==========================
    # USER LEARNING FIRST
    # ==========================
    for key, value in user_map.items():
        if key in narration:
            return value

    # ==========================
    # MASTER LEDGER MATCH
    # ==========================
    for ledger in ledger_list:
        if ledger in narration:
            return ledger

    # ==========================
    # KEYWORD RULES
    # ==========================
    if any(word in narration for word in ["loan", "emi"]):
        return "loan account"

    if any(word in narration for word in ["salary"]):
        return "salary account"

    if any(word in narration for word in ["fuel", "petrol", "hpcl", "indianoil"]):
        return "fuel expense"

    if any(word in narration for word in ["amazon", "flipkart", "swiggy", "zomato"]):
        return "shopping expense"

    if any(word in narration for word in ["upi", "gpay", "phonepe"]):
        return "upi transactions"

    if any(word in narration for word in ["rent"]):
        return "rent expense"

    # ==========================
    # DEFAULT
    # ==========================
    return "suspense"
# ==========================
# MAIN MAPPING FUNCTION
# ==========================
def map_transactions(transactions, master_bytes, supabase, user_id):
    ledger_list = parse_master_html(master_bytes)
    user_map = load_user_mappings(supabase, user_id)

    mapped = []

    for txn in transactions:
        ledger = match_ledger(txn["narration"], ledger_list, user_map)

        mapped_txn = {
            **txn,
            "ledger": ledger
        }

        mapped.append(mapped_txn)

    return mapped
