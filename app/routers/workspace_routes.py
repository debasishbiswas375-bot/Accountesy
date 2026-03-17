from fastapi import APIRouter, UploadFile, File, Request, Form
from fastapi.templating import Jinja2Templates
from app.tools.mapper import smart_map_bank
from app.tools.engine import smart_classify
from app.tools.preview import get_preview_and_cost
import os

router = APIRouter(prefix="/workspace", tags=["Workspace"])
templates = Jinja2Templates(directory="app/templates")

@router.post("/upload")
async def upload_file(request: Request, file: UploadFile = File(...)):
    # 1. Standardize Bank Columns
    content = await file.read()
    df = smart_map_bank(content, file.filename)
    
    # 2. Run AI Classification (Using a hardcoded user_id for now)
    user_id = "debasish_pro_user" 
    df = smart_classify(df, user_id)
    
    # 3. Get Preview & Cost
    analysis = get_preview_and_cost(df)
    
    return templates.TemplateResponse("workspace_preview.html", {
        "request": request,
        "filename": file.filename,
        "total_rows": analysis['total_rows'],
        "cost": analysis['credit_cost'],
        "preview": analysis['preview_data']
    })
@router.post("/final-convert")
async def finalize_conversion(request: Request, filename: str = Form(...)):
    # 1. Deduct credits from user (Logic for your Billing engine later)
    # 2. Call build_tally_xml from converter.py
    # 3. Return the file
    
    from app.tools.converter import build_tally_xml
    # Note: In a real scenario, you'd retrieve the DF from a temporary session or cache
    # For now, we return a success message
    return {"message": f"Credits deducted. {filename} is ready for Tally!"}
