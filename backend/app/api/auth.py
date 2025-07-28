from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
import jwt

router = APIRouter()

SECRET_KEY = "your-secret"

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username != "admin" or form_data.password != "pass":  # Mock
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = jwt.encode({"user": form_data.username}, SECRET_KEY)
    return {"access_token": token}
