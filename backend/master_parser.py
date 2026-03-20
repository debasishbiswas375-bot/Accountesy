from bs4 import BeautifulSoup


DEFAULT_LEDGERS = [
    "Cash",
    "Bank Account",
    "Sales",
    "Purchase",
    "Salary",
    "Rent",
    "Interest Income",
    "Interest Expense",
    "Loan Account",
    "Capital Account",
    "Drawings",
    "Fuel Expense",
    "Electricity Expense",
    "Office Expense",
    "Bank Charges",
    "UPI Transactions",
    "GST Payable",
    "GST Receivable",
    "Suspense"
]


def parse_master_html(html_content: str):
    soup = BeautifulSoup(html_content, "html.parser")
    ledgers = set()

    # Tally XML
    for ledger in soup.find_all("ledger"):
        name = ledger.get("name")
        if name and len(name.strip()) > 2:
            ledgers.add(name.strip())

    # fallback
    if not ledgers:
        for tag in soup.find_all():
            text = tag.get_text(strip=True)
            if text and 2 < len(text) < 50:
                ledgers.add(text)

    return list(set(DEFAULT_LEDGERS) | ledgers)