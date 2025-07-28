from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordBearer
from .api import auth, scans
from .db import engine, Base

app = FastAPI(title="CyberHack AI Backend")

Base.metadata.create_all(bind=engine)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

app.include_router(auth.router, prefix="/auth")
app.include_router(scans.router, prefix="/scans")

@app.get("/")
def root():
    return {"message": "CyberHack AI API"}
