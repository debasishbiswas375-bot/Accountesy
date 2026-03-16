from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

app = FastAPI()

# Tell FastAPI where your CSS/Images are
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Tell FastAPI where your HTML files are
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    # This renders the base.html we just made
    return templates.TemplateResponse("base.html", {"request": request})

# A simple route for the converter to test the links later
@app.get("/converter", response_class=HTMLResponse)
async def converter(request: Request):
    return templates.TemplateResponse("base.html", {"request": request, "header": "Tally Converter"})
