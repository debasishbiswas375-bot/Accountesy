from fastapi import APIRouter, UploadFile, File
from fastapi.responses import FileResponse
import os
import pandas as pd

from app.tools.engine import process_pdf_to_excel

router = APIRouter()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# =========================
# PDF → EXCEL
# =========================
@router.post("/workspace/convert-excel")
async def convert_excel(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    output_file = process_pdf_to_excel(file_path, user_id="guest")

    return FileResponse(output_file, filename=os.path.basename(output_file))


# =========================
# PDF → XML
# =========================
@router.post("/workspace/convert-xml")
async def convert_xml(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    df = pd.read_excel(process_pdf_to_excel(file_path))

    output_xml = file_path.replace(".pdf", ".xml")

    with open(output_xml, "w") as f:
        f.write("<xml>Converted</xml>")

    return FileResponse(output_xml, filename=os.path.basename(output_xml))
