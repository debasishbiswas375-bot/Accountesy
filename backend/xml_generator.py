from datetime import datetime

def format_date(date_str):
    try:
        return datetime.strptime(date_str, "%d-%b-%y").strftime("%Y%m%d")
    except:
        return "20260201"


def generate_xml(data):
    xml = """<ENVELOPE>
<HEADER><TALLYREQUEST>Import Data</TALLYREQUEST></HEADER>
<BODY><IMPORTDATA><REQUESTDESC><REPORTNAME>Vouchers</REPORTNAME></REQUESTDESC><REQUESTDATA>
"""

    for txn in data:
        ledger = txn["final_ledger"]
        bank = txn["bank"]
        amount = float(txn["amount"])
        narration = txn["narration"]
        date = format_date(txn["date"])

        if txn["type"] == "receipt":
            xml += f"""
<VOUCHER VCHTYPE="Receipt">
<DATE>{date}</DATE>
<NARRATION>{narration}</NARRATION>

<ALLLEDGERENTRIES.LIST>
<LEDGERNAME>{bank}</LEDGERNAME>
<AMOUNT>{amount}</AMOUNT>
</ALLLEDGERENTRIES.LIST>

<ALLLEDGERENTRIES.LIST>
<LEDGERNAME>{ledger}</LEDGERNAME>
<AMOUNT>-{amount}</AMOUNT>
</ALLLEDGERENTRIES.LIST>

</VOUCHER>
"""
        else:
            xml += f"""
<VOUCHER VCHTYPE="Payment">
<DATE>{date}</DATE>
<NARRATION>{narration}</NARRATION>

<ALLLEDGERENTRIES.LIST>
<LEDGERNAME>{ledger}</LEDGERNAME>
<AMOUNT>{amount}</AMOUNT>
</ALLLEDGERENTRIES.LIST>

<ALLLEDGERENTRIES.LIST>
<LEDGERNAME>{bank}</LEDGERNAME>
<AMOUNT>-{amount}</AMOUNT>
</ALLLEDGERENTRIES.LIST>

</VOUCHER>
"""

    xml += "</REQUESTDATA></IMPORTDATA></BODY></ENVELOPE>"
    return xml

def generate_tally_xml(data):
    return generate_xml(data)
