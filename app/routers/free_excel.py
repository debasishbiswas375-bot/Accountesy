from fastapi import APIRouter, UploadFile, File
from fastapi.responses import FileResponse
from app.tools.mapper import smart_map_bank
import pandas as pd
import uuid, os

router = APIRouter()

TEMP_DIR = "app/temp"
os.makedirs(TEMP_DIR, exist_ok=True)

# =========================
# FREE EXCEL CONVERT
# =========================
@router.post("/convert-excel")
async def convert_excel(file: UploadFile = File(...)):
    content = await file.read()

    df = smart_map_bank(content, file.filename)

    output_path = os.path.join(TEMP_DIR, f"{uuid.uuid4()}.xlsx")

    df.to_excel(output_path, index=False)

    return FileResponse(output_path, filename="converted.xlsx")
