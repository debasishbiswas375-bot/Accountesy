import pandas as pd
import re

def detect_bank(text):
    text = text.lower()

    if "state bank of india" in text or "sbin" in text:
        return "SBI"
    elif "icici" in text:
        return "ICICI"
    elif "hdfc" in text:
        return "HDFC"
    elif "axis" in text:
        return "AXIS"
    else:
        return "UNKNOWN"


def parse_sbi(lines):
    data = []
    current = None

    date_pattern = r"\d{2}/\d{2}/\d{4}"

    for line in lines:
        line = line.strip()

        # NEW ROW
        if re.match(date_pattern, line):
            if current:
                data.append(current)

            current = {
                "date": line.split()[0],
                "description": "",
                "debit": 0,
                "credit": 0,
                "balance": 0
            }

        elif current:
            # append description
            current["description"] += " " + line

            # detect amounts
            amounts = re.findall(r"\d{1,3}(?:,\d{3})*\.\d{2}", line)

            if len(amounts) >= 2:
                amt = float(amounts[0].replace(",", ""))
                bal = float(amounts[-1].replace(",", ""))

                current["balance"] = bal

                if "to transfer" in line.lower():
                    current["debit"] = amt
                else:
                    current["credit"] = amt

    if current:
        data.append(current)

    return pd.DataFrame(data)


def clean_description(desc):
    desc = str(desc)

    # remove junk
    desc = re.sub(r"NEFT.*?\*", "", desc)
    desc = re.sub(r"IN\d+", "", desc)

    return desc.strip()


def process_df(df):
    df = df.copy()
    df["description"] = df["description"].apply(clean_description)
    return df


def build_summary(df):
    return pd.DataFrame({
        "Metric": ["Total Transactions", "Total Credit", "Total Debit"],
        "Value": [
            len(df),
            df["credit"].sum(),
            df["debit"].sum()
        ]
    })


def run_free_engine(file_content, filename):
    import pdfplumber

    text = ""

    with pdfplumber.open(file_content) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"

    lines = text.split("\n")

    bank = detect_bank(text)

    if bank == "SBI":
        raw_df = parse_sbi(lines)
    else:
        raw_df = parse_sbi(lines)  # fallback

    processed_df = process_df(raw_df)
    summary_df = build_summary(processed_df)

    return raw_df, processed_df, summary_df
