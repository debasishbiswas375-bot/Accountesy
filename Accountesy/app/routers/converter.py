from fastapi import APIRouter, UploadFile, File, HTTPException
import pandas as pd
import io
# Import directly from the mapper file in the logic folder
from logic.mapper import intelligent_header_mapping

router = APIRouter(prefix="/convert", tags=["Converter"])

@router.post("/")
async def convert_statement(file: UploadFile = File(...)):
    contents = await file.read()
    df = pd.read_excel(io.BytesIO(contents))
    
    # This runs the 100+ bank variation logic
    df = intelligent_header_mapping(df)
    
    return {"status": "success", "rows": len(df)}
