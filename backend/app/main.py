from fastapi import FastAPI
from fastapi.responses import FileResponse
from .api.health import router as health_router
from .api.scans import router as scans_router
from .core.db import engine
from .models.scan import Base  # noqa: F401

app = FastAPI(title="CyberHack AI")

# create tables on startup
Base.metadata.create_all(bind=engine)

app.include_router(health_router, prefix="/healthz", tags=["health"])
app.include_router(scans_router, prefix="/scan", tags=["scan"])

@app.get("/")
def root():
    return {"ok": True}

@app.get("/ui")
def ui():
    return FileResponse("backend/app/static/index.html")
