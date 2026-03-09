import pandas as pd

def parse_excel(file):

    df = pd.read_excel(file)

    vouchers=[]

    for _,row in df.iterrows():

        vouchers.append({
            "date":str(row.get("Date")),
            "narration":str(row.get("Narration")),
            "amount":row.get("Debit") or row.get("Credit")
        })

    return vouchers
