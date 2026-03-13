from fastapi import APIRouter, UploadFile, File, Request
from fastapi.templating import Jinja2Templates
import pandas as pd
import pdfplumber

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.post("/convert")
async def convert(
    request: Request,
    statement: UploadFile = File(...),
    ledger: UploadFile = File(None)
):

    filename = statement.filename

    if filename.endswith(".xlsx") or filename.endswith(".xls"):
        df = pd.read_excel(statement.file)

    elif filename.endswith(".csv"):
        df = pd.read_csv(statement.file)

    elif filename.endswith(".pdf"):
        with pdfplumber.open(statement.file) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text()

        df = pd.DataFrame({"text": [text]})

    else:
        df = pd.DataFrame()

    # AI mapping placeholder
    result = df.head(20).to_html()

    return templates.TemplateResponse(
        "workspace.html",
        {
            "request": request,
            "result": result
        }
    )
