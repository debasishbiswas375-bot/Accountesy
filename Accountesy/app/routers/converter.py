from fastapi import APIRouter, UploadFile, File, HTTPException
import pandas as pd
import io
# FIXED IMPORT: Points directly to your logic folder
from logic.mapper import intelligent_header_mapping

router = APIRouter(prefix="/convert", tags=["Converter"])

@router.post("/")
async def convert_statement(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))
        
        # This triggers the 100+ bank variation mapping
        df = intelligent_header_mapping(df)
        
        return {"status": "success", "processed_rows": len(df)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
