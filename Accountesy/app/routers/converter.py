from fastapi import APIRouter, UploadFile, File
import pandas as pd

router = APIRouter()


@router.post("/convert")
async def convert(statement: UploadFile = File(...)):

    df = pd.read_excel(statement.file)

    vouchers = []

    for _, row in df.iterrows():

        vouchers.append({
            "narration": str(row[0]),
            "ledger": "Suspense"
        })

    return {"vouchers": vouchers}
