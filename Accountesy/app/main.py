import sys
import os
import io
from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import StreamingResponse

# --- PATH CONFIGURATION ---
app_dir = os.path.dirname(os.path.abspath(__file__)) 
if app_dir not in sys.path:
    sys.path.append(app_dir)

# Importing rectified logic names
from logic.processor import get_preview_data, generate_tally_xml

app = FastAPI(title="Accountesy")

root_dir = os.path.dirname(app_dir) 
app.mount("/static", StaticFiles(directory=os.path.join(root_dir, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(root_dir, "templates"))

@app.get("/")
async def landing(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})

@app.get("/workspace")
async def workspace(request: Request):
    return templates.TemplateResponse("workspace.html", {"request": request})

@app.post("/convert/preview")
async def preview_logic(bank_file: UploadFile = File(...), master_file: UploadFile = File(...)):
    try:
        # Generates JSON for the drag-and-drop preview table
        preview_results, masters = await get_preview_data(bank_file, master_file)
        return {"transactions": preview_results, "master_ledgers": masters}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/convert/final")
async def final_export(request: Request):
    try:
        data = await request.json()
        xml_data = generate_tally_xml(data['transactions'])
        return StreamingResponse(
            io.BytesIO(xml_data.encode('utf-8')), 
            media_type="application/xml",
            headers={"Content-Disposition": "attachment; filename=Accountesy_Final_Import.xml"}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
