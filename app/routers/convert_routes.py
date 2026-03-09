from fastapi import APIRouter, UploadFile, File
import pandas as pd

router = APIRouter()

@router.post("/convert")

async def convert(file: UploadFile = File(...)):

    df = pd.read_excel(file.file)

    rows = len(df)

    return {
        "status": "converted",
        "rows": rows
    }
