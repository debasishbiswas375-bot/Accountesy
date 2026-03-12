from fastapi import APIRouter, UploadFile, File
from app.logic.processor import process_statement

router = APIRouter()

@router.post("/convert")
async def convert(statement: UploadFile = File(...), master: UploadFile | None = File(None)):
    return process_statement(statement, master)

