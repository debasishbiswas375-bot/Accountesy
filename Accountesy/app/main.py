import os
import io
from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import StreamingResponse

# Import our processing engine (which we will create next)
from logic.processor import process_tally_conversion

app = FastAPI(title="Accountesy")

# Path setup for Render
app_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(app_dir)
app.mount("/static", StaticFiles(directory=os.path.join(root_dir, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(root_dir, "templates"))

@app.get("/")
async def landing(request: Request): return templates.TemplateResponse("landing.html", {"request": request})

@app.get("/workspace")
async def workspace(request: Request): return templates.TemplateResponse("workspace.html", {"request": request})

@app.post("/convert/process")
async def handle_upload(bank_file: UploadFile = File(...), master_file: UploadFile = File(...)):
    try:
        # Pass files to the pure logic processor
        xml_data = await process_tally_conversion(bank_file, master_file)
        return StreamingResponse(
            io.BytesIO(xml_data), 
            media_type="application/xml",
            headers={"Content-Disposition": "attachment; filename=Accountesy_Import.xml"}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
