import time
from typing import List, Optional
from fastapi import APIRouter, Query, BackgroundTasks, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..core.db import SessionLocal
from ..models.scan import Scan

router = APIRouter()

# --- legacy demo endpoint (kept) ---
@router.get("/vuln")
def scan_vuln(target: str = Query(..., min_length=1)):
    return {"target": target, "result": "mock"}

# --- DTOs ---
class ScanCreate(BaseModel):
    target: str

class ScanOut(BaseModel):
    id: int
    target: str
    status: str
    result: Optional[dict] = None
    created_at: str

    @classmethod
    def from_model(cls, s: Scan):
        return cls(
            id=s.id,
            target=s.target,
            status=s.status,
            result=s.result,
            created_at=s.created_at.isoformat() + "Z",
        )

# --- helpers ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

import os, requests
TOOLS_URL = os.getenv("TOOLS_URL", "http://tools:9000")

import os, requests
TOOLS_URL = os.getenv("TOOLS_URL", "http://tools:9000")

import os, requests
TOOLS_URL = os.getenv("TOOLS_URL", "http://tools:9000")

import os, requests
TOOLS_URL = os.getenv("TOOLS_URL", "http://tools:9000")

import os, requests
TOOLS_URL = os.getenv("TOOLS_URL", "http://tools:9000")

import os, requests
TOOLS_URL = os.getenv("TOOLS_URL", "http://tools:9000")

def run_scan_job(scan_id: int):
    # mock "work"
    with SessionLocal() as db:
        s = db.get(Scan, scan_id)
        if not s:
            return
        s.status = "running"
        db.commit()
    # call tools-runner safely (fixed command inside runner)
    try:
        r = requests.post(f"{TOOLS_URL}/run", json={"tool":"nmap","target": s.target})
        r.raise_for_status()
        data = r.json()
        result = {"tool": "nmap", **data.get("parsed", {})}
    except Exception as e:
        result = {"tool":"nmap","error": str(e)}
    with SessionLocal() as db:
        s = db.get(Scan, scan_id)
        if not s:
            return
        s.status = "done"
        s.result = result
        db.commit()

# --- routes ---
@router.post("/scans", response_model=ScanOut, status_code=201)
def create_scan(payload: ScanCreate, bg: BackgroundTasks):
    with SessionLocal() as db:
        s = Scan(target=payload.target, status="running")
        db.add(s)
        db.commit()
        db.refresh(s)
        bg.add_task(run_scan_job, s.id)
        return ScanOut.from_model(s)

@router.get("/scans", response_model=List[ScanOut])
def list_scans():
    with SessionLocal() as db:
        rows = db.execute(select(Scan).order_by(Scan.id.desc()).limit(50)).scalars().all()
        return [ScanOut.from_model(r) for r in rows]

@router.get("/scans/{scan_id}", response_model=ScanOut)
def get_scan(scan_id: int):
    with SessionLocal() as db:
        s = db.get(Scan, scan_id)
        if not s:
            raise HTTPException(status_code=404, detail="Scan not found")
        return ScanOut.from_model(s)
