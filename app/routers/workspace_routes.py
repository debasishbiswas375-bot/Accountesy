from fastapi import APIRouter, UploadFile, File
from app.parser import parse_bank_statement
from app.ai_ledger import detect_ledger

router = APIRouter()

@router.post("/convert")
async def convert(file: UploadFile = File(...)):
    txs = parse_bank_statement(file.file)
    vouchers=[]
    for tx in txs:
        ledger = detect_ledger(tx["narration"])
        vouchers.append({
            "date":tx["date"],
            "narration":tx["narration"],
            "ledger":ledger,
            "amount":tx["debit"] or tx["credit"]
        })
    return {"vouchers":vouchers}
