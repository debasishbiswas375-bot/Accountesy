from fastapi import APIRouter,Form
import bcrypt

router=APIRouter()

@router.post("/login")
def login(email:str=Form(...),password:str=Form(...)):
 return {"status":"login success"}

@router.post("/register")
def register(email:str=Form(...),password:str=Form(...)):
 hashed=bcrypt.hashpw(password.encode(),bcrypt.gensalt())
 return {"status":"registered"}
