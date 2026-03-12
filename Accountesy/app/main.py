import sys
import os
import io
from fastapi import FastAPI, Request, UploadFile, File, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.middleware.sessions import SessionMiddleware

# --- 1. PATH & DATABASE CONFIG ---
app_dir = os.path.dirname(os.path.abspath(__file__)) 
if app_dir not in sys.path:
    sys.path.append(app_dir)

from logic.processor import get_preview_data, generate_tally_xml, save_pattern
from database import supabase # Uses your Render Environment Keys
from dependencies import get_current_user, check_credit_eligibility

app = FastAPI(title="Accountesy AI Engine")

# SECURITY: Use the SECRET_KEY from your Render dashboard
app.add_middleware(SessionMiddleware, secret_key=os.environ.get("SECRET_KEY", "fallback-secret"))

# Setup Static and Templates
root_dir = os.path.dirname(app_dir) 
app.mount("/static", StaticFiles(directory=os.path.join(root_dir, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(root_dir, "templates"))

class LearningData(BaseModel):
    narration: str
    ledger: str

# --- 2. PAGE NAVIGATION ROUTES ---

@app.get("/")
async def landing(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})

@app.get("/")
async def dashboard(request: Request, user=Depends(get_current_user)):
    """Fetches user-wise data only"""
    user_record = supabase.table("users").select("*").eq("id", user.id).single().execute()
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user_name": user_record.data.get('full_name', 'User'),
        "credits": user_record.data.get('credits', 0.00)
    })})

@app.get("/workspace")
async def workspace(request: Request):
    return templates.TemplateResponse("workspace.html", {"request": request})

@app.get("/history")
async def history(request: Request):
    return templates.TemplateResponse("history.html", {"request": request})

@app.get("/account")
async def account(request: Request):
    return templates.TemplateResponse("account.html", {"request": request})
    })

@app.get("/pricing")
async def pricing(request: Request):
    # DYNAMIC: Fetch plans directly from Supabase
    try:
        response = supabase.table("plans").select("*").eq("active", True).order("price").execute()
        plans = response.data
    except:
        plans = [] # Fallback
    
    return templates.TemplateResponse("pricing.html", {"request": request, "plans": plans})

# --- 3. AI & CREDIT ENGINE API ---

@app.post("/convert/preview")
async def preview_api(bank_file: UploadFile = File(...), master_file: UploadFile = File(None)):
    try:
        transactions, _ = await get_preview_data(bank_file, master_file)
        return {"transactions": transactions}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/convert/final")
async def final_api(request: Request):
    """Checks credits (0.1/vch) and generates Tally XML"""
    try:
        data = await request.json()
        
        # Security: Check credit eligibility before processing
        # await check_credit_eligibility(user_id, len(data['transactions']))

        xml_str, credit_cost, compressed_data = generate_tally_xml(
            data['transactions'], 
            data.get('bank_name', 'Bank Account')
        )
        
        return JSONResponse({
            "xml": xml_str,
            "credits_used": credit_cost,
            "voucher_count": len(data['transactions']),
            "status": "Available"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/learn")
async def learn_api(data: LearningData):
    try:
        save_pattern(data.narration, data.ledger)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- 4. RENDER BINDING ---
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)

