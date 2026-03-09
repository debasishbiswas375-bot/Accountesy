from fastapi import APIRouter,Request
from fastapi.templating import Jinja2Templates

router=APIRouter()
templates=Jinja2Templates(directory="app/templates")

@router.get("/dashboard")
def dashboard(request:Request):

 data={
  "plan":"Starter",
  "credits":100,
  "expiry":"2026-04-01",
  "conversions":12
 }

 return templates.TemplateResponse("dashboard.html",{"request":request,"data":data})
