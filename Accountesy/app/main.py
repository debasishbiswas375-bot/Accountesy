import sys
import os
import io
from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# --- 1. PATH CONFIGURATION ---
app_dir = os.path.dirname(os.path.abspath(__file__)) 
if app_dir not in sys.path:
    sys.path.append(app_dir)

# Import the logic from your processor
from logic.processor import get_preview_data, generate_tally_xml, save_pattern

app = FastAPI(title="Accountesy AI Engine")

# Setup Static and Templates
root_dir = os.path.dirname(app_dir) 
app.mount("/static", StaticFiles(directory=os.path.join(root_dir, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(root_dir, "templates"))

# Data model for AI Learning
class LearningData(BaseModel):
    narration: str
    ledger: str

# --- 2. PAGE ROUTES (Mapping your templates) ---

@app.get("/")
async def landing(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})

@app.get("/workspace")
async def workspace(request: Request):
    return templates.TemplateResponse("workspace.html", {"request": request})

@app.get("/history")
async def history(request: Request):
    return templates.TemplateResponse("history.html", {"request": request})

@app.get("/login")
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register")
async def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/account")
async def account(request: Request):
    return templates.TemplateResponse("account.html", {"request": request})

@app.get("/pricing")
async def pricing(request: Request):
    return templates.TemplateResponse("pricing.html", {"request": request})

# --- 3. AI & CREDIT API ROUTES ---

@app.post("/convert/preview")
async def preview_api(bank_file: UploadFile = File(...), master_file: UploadFile = File(None)):
    """Processes the upload and returns AI suggestions."""
    try:
        transactions, _ = await get_preview_data(bank_file, master_file)
        return {"transactions": transactions}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/convert/final")
async def final_api(request: Request):
    """Generates Tally XML and calculates $0.1 credit deduction."""
    try:
        data = await request.json()
        # Generate the XML and the credit math
        xml_str, credit_cost, compressed_data = generate_tally_xml(
            data['transactions'], 
            data.get('bank_name', 'Bank Account')
        )
        
        # We return JSON so the workspace can show the Credit Deduction alert
        return JSONResponse({
            "xml": xml_str,
            "credits_used": credit_cost,
            "count": len(data['transactions'])
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/learn")
async def learn_api(data: LearningData):
    """The Auto-Learning Endpoint."""
    try:
        save_pattern(data.narration, data.ledger)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- 4. RENDER DEPLOYMENT BINDING ---
if __name__ == "__main__":
    import uvicorn
    # Render provides a PORT environment variable
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
