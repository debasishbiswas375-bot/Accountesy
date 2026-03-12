import pandas as pd
from app.logic.mapper import parse_master

learning_memory = {}

def process_statement(statement, master):

    ledgers = []

    if master:
        html = master.file.read().decode()
        ledgers = parse_master(html)

    df = pd.read_excel(statement.file)

    vouchers = []

    for _, row in df.iterrows():

        narration = str(row[0]).lower()
        ledger = None

        # priority 1 master
        for l in ledgers:
            if l in narration:
                ledger = l
                break

        # priority 2 learned ai
        if not ledger:
            for k, v in learning_memory.items():
                if k in narration:
                    ledger = v

        # priority 3 suspense
        if not ledger:
            ledger = "Suspense"

        vouchers.append({
            "narration": narration,
            "ledger": ledger
        })

    return {"vouchers": vouchers}
