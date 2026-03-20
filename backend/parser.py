import pdfplumber


def clean_amount(val):
    if not val:
        return 0.0
    val = str(val).replace(",", "").strip()
    try:
        return float(val)
    except:
        return 0.0


def parse_transactions(file_stream):
    transactions = []

    with pdfplumber.open(file_stream) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()

            for table in tables:
                for row in table:
                    if not row or len(row) < 5:
                        continue

                    row_str = " ".join([str(x) for x in row if x])

                    # skip header
                    if "Date" in row_str and "Balance" in row_str:
                        continue

                    try:
                        # ✅ SBI FORMAT FIX
                        date = str(row[0]).strip()
                        narration = str(row[2]).strip()  # ✅ CORRECT COLUMN
                        debit = clean_amount(row[3])
                        credit = clean_amount(row[4])

                        # skip empty rows
                        if not narration or narration.lower() == "nan":
                            continue

                        amount = credit if credit > 0 else -debit

                        transactions.append({
                            "date": date,
                            "narration": narration,
                            "debit": debit,
                            "credit": credit,
                            "amount": amount
                        })

                    except Exception:
                        continue

    return transactions
    def parse_statement(file_path):
    return parse_transactions(file_path)
