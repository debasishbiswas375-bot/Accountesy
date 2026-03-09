from fastapi import APIRouter

router=APIRouter()

@router.get("/plans")
def plans():
 return [
  {"name":"Free","credits":10,"price":0},
  {"name":"Starter","credits":100,"price":99},
  {"name":"Pro","credits":500,"price":399},
  {"name":"Enterprise","credits":2000,"price":999}
 ]
