import sys
import os
import io
from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# --- 1. PATH CONFIGURATION ---
# Ensures the app can find the 'logic' folder even on Render
app_dir = os.path.dirname(os.path.abspath(__file__)) 
if app_dir not in sys.path:
    sys.path.append(app_dir)

# Import the core logic from your processor.py
from logic.processor import get_preview_data, generate_tally_xml, save_pattern

app = FastAPI(title="Accountesy AI Engine")

# Setup Static files (CSS/Images) and Jinja2 Templates
root_dir = os.path.dirname(app_dir) 
app.mount("/static", StaticFiles(directory=os.path.join(root_dir, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(root_dir, "templates"))

# Data model for the AI Learning API
class LearningData(BaseModel):
    narration: str
    ledger: str

# --- 2. PAGE NAVIGATION ROUTES ---

@app.get("/")
async def landing(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})

@app.get("/dashboard")
async def dashboard(request: Request):
    # In production, fetch these from Supabase:
    # stats = {
    #     "balance": 9999.00,
    #     "total_converted": 1250,
    #     "patterns_learned": 84,
    #     "recent_activity": [...] 
    # }
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user_name": "Debasish Biswas",
        "credits": 9999.00,
        "vouchers_processed": 1248,
        "learned_count": 84
    })

@app.get("/workspace")
async def workspace(request: Request):
    return templates.TemplateResponse("workspace.html", {"request": request})

@app.get("/history")
async def history(request: Request):
    return templates.TemplateResponse("history.html", {"request": request})

@app.get("/account")
async def account(request: Request):
    # This maps to the user data seen in your Supabase screenshot
    return templates.TemplateResponse("account.html", {
        "request": request,
        "user_name": "Debasish Biswas",
        "user_email": "debasish.biswas375@gmail.com",
        "user_credits": 9999.00
    })

@app.get("/pricing")
async def pricing(request: Request):
    # In production, use your supabase client:
    # response = supabase.table("plans").select("*").eq("active", True).order("price").execute()
    # plans = response.data
    
    # Mock data based on your Supabase Screenshot
    plans = [
        {"name": "Free", "credits": 10, "price": 0, "duration_days": 30, "description": "10 Credits Included, Standard Processing"},
        {"name": "Starter", "credits": 100, "price": 99, "duration_days": 30, "description": "100 Credits, AI Learning Access"},
        {"name": "Pro", "credits": 500, "price": 399, "duration_days": 30, "description": "500 Credits, Priority AI Processing"},
        {"name": "Enterprise", "credits": 2000, "price": 999, "duration_days": 30, "description": "2000 Credits, Multi-user Access"}
    ]
    
    return templates.TemplateResponse("pricing.html", {
        "request": request,
        "plans": plans
    })

@app.get("/login")
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register")
async def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

# --- 3. AI & CREDIT ENGINE API ---

@app.post("/convert/preview")
async def preview_api(bank_file: UploadFile = File(...), master_file: UploadFile = File(None)):
    """Step 1: AI scans the file and suggests ledgers in the table."""
    try:
        transactions, _ = await get_preview_data(bank_file, master_file)
        return {"transactions": transactions}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/convert/final")
async def final_api(request: Request):
    """Step 2: Generate XML and calculate the 0.1 credit deduction."""
    try:
        data = await request.json()
        
        # Get XML string and credit math from processor.py
        xml_str, credit_cost, compressed_data = generate_tally_xml(
            data['transactions'], 
            data.get('bank_name', 'Bank Account')
        )
        
        # Return data matching your conversion_history table columns
        return JSONResponse({
            "xml": xml_str,
            "credits_used": credit_cost,
            "voucher_count": len(data['transactions']),
            "status": "Available"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@app.post("/learn")
async def learn_api(data: LearningData):
    """Step 3: Save manual 'Nil' corrections to the AI memory."""
    try:
        save_pattern(data.narration, data.ledger)
        return {"status": "success", "message": "Pattern learned successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- 4. RENDER / LOCAL BINDING ---
if __name__ == "__main__":
    import uvicorn
    # PORT is dynamically assigned by Render; defaults to 10000 locally
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)


