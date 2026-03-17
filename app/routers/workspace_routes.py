from fastapi import APIRouter, UploadFile, File
from app.database import supabase

router = APIRouter(prefix="/workspace", tags=["Workspace"])

@router.post("/convert")
async def handle_conversion(file: UploadFile = File(...)):
    # Read the file data
    content = await file.read()
    
    # Logic to process the bank statement will go into Category 7
    print(f"Pro Plan File Received: {file.filename}")
    
    # For now, we return a success status
    return {
        "status": "success",
        "filename": file.filename,
        "message": "Processing started. Check history for results soon."
    }
