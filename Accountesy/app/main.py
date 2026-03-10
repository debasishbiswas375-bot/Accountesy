import sys
import os
import io
from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import StreamingResponse

# --- 1. PATH CONFIGURATION ---
# Adds the 'app' directory to sys.path so the 'logic' module can be found
app_dir = os.path.dirname(os.path.abspath(__file__)) 
if app_dir not in sys.path:
    sys.path.append(app_dir)

# Now we can safely import your logic processor
from logic.processor import process_tally_conversion

app = FastAPI(title="Accountesy")

# Forces static/templates paths to the root folder for Render stability
root_dir = os.path.dirname(app_dir) 
app.mount("/static", StaticFiles(directory=os.path.join(root_dir, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(root_dir, "templates"))

# --- 2. PAGE ROUTES ---
@app.get("/")
async def landing(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})

@app.get("/workspace")
async def workspace(request: Request):
    return templates.TemplateResponse("workspace.html", {"request": request})

@app.get("/history")
async def history(request: Request):
    return templates.TemplateResponse("history.html", {"request": request})

@app.get("/account")
async def account(request: Request):
    return templates.TemplateResponse("account.html", {"request": request})

# --- 3. THE RECTIFIED CONVERSION ENDPOINT ---
@app.post("/convert/process")
async def handle_upload(bank_file: UploadFile = File(...), master_file: UploadFile = File(...)):
    """
    Receives files and passes them to the logic processor.
    Handles the float conversion and skip-header logic internally.
    """
    try:
        # Calls the heavy-lifting logic from logic/processor.py
        xml_data = await process_tally_conversion(bank_file, master_file)
        
        return StreamingResponse(
            io.BytesIO(xml_data), 
            media_type="application/xml",
            headers={
                "Content-Disposition": f"attachment; filename=Accountesy_{bank_file.filename}.xml"
            }
        )
    except Exception as e:
        # Catches 'string to float' or 'Invalid tag' errors and reports them
        raise HTTPException(status_code=400, detail=str(e))

# --- 4. RENDER PORT BINDING ---
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
