from fastapi import FastAPI
from fastapi.responses import FileResponse
from sqlalchemy import text
from .api.health import router as health_router
from .api.scans import router as scans_router
from .core.db import engine
from .models.scan import Base  # noqa

app = FastAPI(title="CyberHack AI")

# create tables
Base.metadata.create_all(bind=engine)

# tiny migration: ensure 'tool' column exists
with engine.begin() as conn:
    try:
        conn.execute(text("ALTER TABLE scans ADD COLUMN IF NOT EXISTS tool VARCHAR(32) NOT NULL DEFAULT 'nmap'"))
    except Exception:
        pass

app.include_router(health_router, prefix="/healthz", tags=["health"])
app.include_router(scans_router, prefix="/scan", tags=["scan"])

@app.get("/")
def root():
    return {"ok": True}

@app.get("/ui")
def ui():
    return FileResponse("backend/app/static/index.html")

from fastapi import FastAPI
import os
app = globals().get("app") or FastAPI()
@app.get("/health")
def health():
    return {"status": "ok", "mode": "dry-run" if os.getenv("DRY_RUN")=="1" else "normal"}
