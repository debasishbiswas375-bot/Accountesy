import sys, os, io
from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# --- 1. PATH & IMPORT CONFIG ---
app_dir = os.path.dirname(os.path.abspath(__file__)) 
if app_dir not in sys.path: sys.path.append(app_dir)

# Import the Brain (Processor) and the Memory function
from logic.processor import get_preview_data, generate_tally_xml, save_pattern

app = FastAPI(title="Accountesy AI")

root_dir = os.path.dirname(app_dir) 
app.mount("/static", StaticFiles(directory=os.path.join(root_dir, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(root_dir, "templates"))

# Data Model for the Learning Route
class LearningData(BaseModel):
    narration: str
    ledger: str

# --- 2. NAVIGATION ROUTES ---
@app.get("/")
async def landing(request: Request): return templates.TemplateResponse("landing.html", {"request": request})

@app.get("/login")
async def login(request: Request): return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register")
async def register(request: Request): return templates.TemplateResponse("register.html", {"request": request})

@app.get("/workspace")
async def workspace(request: Request): return templates.TemplateResponse("workspace.html", {"request": request})

@app.get("/dashboard")
async def dashboard(request: Request): return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/history")
async def history(request: Request): return templates.TemplateResponse("history.html", {"request": request})

@app.get("/account")
async def account(request: Request): return templates.TemplateResponse("account.html", {"request": request})

@app.get("/pricing")
async def pricing(request: Request): return templates.TemplateResponse("pricing.html", {"request": request})

@app.get("/admin")
async def admin_panel(request: Request): return templates.TemplateResponse("admin.html", {"request": request})

# --- 3. AI & AUTOMATION ROUTES ---

@app.post("/convert/preview")
async def preview_logic(bank_file: UploadFile = File(...), master_file: UploadFile = File(None)):
    try:
        results, masters = await get_preview_data(bank_file, master_file)
        return {"transactions": results, "master_ledgers": masters}
    except Exception as e: raise HTTPException(status_code=400, detail=str(e))

@app.post("/convert/final")
async def final_export(request: Request):
    try:
        data = await request.json()
        xml_data = generate_tally_xml(data['transactions'], data.get('bank_name', 'Bank Account'))
        return StreamingResponse(io.BytesIO(xml_data.encode('utf-8')), media_type="application/xml")
    except Exception as e: raise HTTPException(status_code=400, detail=str(e))

# --- NEW: THE LEARNING ROUTE ---
@app.post("/learn")
async def learn_pattern(data: LearningData):
    """
    This endpoint allows the Workspace to 'Teach' the AI.
    When you Nil a suspense, the JS calls this to save the pattern.
    """
    try:
        save_pattern(data.narration, data.ledger)
        return {"status": "success", "message": "AI learned a new pattern!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- 4. RENDER PORT BINDING ---
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
