import pandas as pd

def parse_bank_statement(file):
    df = pd.read_excel(file)
    transactions=[]
    for _,row in df.iterrows():
        transactions.append({
            "date":row.get("Date"),
            "narration":row.get("Narration"),
            "debit":row.get("Debit"),
            "credit":row.get("Credit")
        })
    return transactions
