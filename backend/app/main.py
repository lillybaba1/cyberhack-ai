from fastapi import FastAPI
from .api.health import router as health_router
from .api.scans import router as scans_router

app = FastAPI(title="CyberHack AI")

app.include_router(health_router, prefix="/healthz", tags=["health"])
app.include_router(scans_router, prefix="/scan", tags=["scan"])

@app.get("/")
def root():
    return {"ok": True}
