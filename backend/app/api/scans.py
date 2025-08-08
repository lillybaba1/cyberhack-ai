import os, subprocess

DRY_RUN = os.getenv("DRY_RUN") == "1"

def run_cmd(cmd, timeout=60):
    if DRY_RUN:
        return subprocess.CompletedProcess(cmd, 0, stdout="{}", stderr="")
    return run_cmd(cmd, capture_output=True, text=True, timeout=timeout)

import time, os, requests
from typing import List, Optional
from fastapi import APIRouter, Query, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select, delete
from sqlalchemy.orm import Session
from ..core.db import SessionLocal
from ..models.scan import Scan

router = APIRouter()
TOOLS_URL = os.getenv("TOOLS_URL", "http://tools:9000")

@router.get("/vuln")
def scan_vuln(target: str = Query(..., min_length=1)):
    return {"target": target, "result": "mock"}

class ScanCreate(BaseModel):
    target: str = Field(..., min_length=1)
    tool: str = Field(default="nmap")

class ScanOut(BaseModel):
    id: int
    target: str
    tool: str
    status: str
    result: Optional[dict] = None
    created_at: str

    @classmethod
    def from_model(cls, s: Scan):
        return cls(
            id=s.id,
            target=s.target,
            tool=s.tool,
            status=s.status,
            result=s.result,
            created_at=s.created_at.isoformat() + "Z",
        )

def run_scan_job(scan_id: int):
    with SessionLocal() as db:
        s = db.get(Scan, scan_id)
        if not s:
            return
        s.status = "running"
        db.commit()

    try:
        r = requests.post(f"{TOOLS_URL}/run", json={"tool": s.tool, "target": s.target}, timeout=600)
        r.raise_for_status()
        data = r.json()
        result = {
            "tool": s.tool,
            **{k: v for k, v in data.items() if k in ("parsed","stdout","stderr","headers","subdomains")},
            "ok": data.get("ok", True)
        }
        status = "done" if data.get("ok", True) else "error"
    except Exception as e:
        result = {"tool": s.tool, "error": str(e)}
        status = "error"

    with SessionLocal() as db:
        s = db.get(Scan, scan_id)
        if not s:
            return
        s.status = status
        s.result = result
        db.commit()

@router.post("/scans", response_model=ScanOut, status_code=201)
def create_scan(payload: ScanCreate, bg: BackgroundTasks):
    tool = payload.tool.lower().strip()
    if tool not in {"nmap","whatweb","nikto","sqlmap","dirb","theharvester","amass","dnsenum","curl"}:
        raise HTTPException(status_code=400, detail="unsupported tool")
    with SessionLocal() as db:
        s = Scan(target=payload.target.strip(), tool=tool, status="running")
        db.add(s)
        db.commit()
        db.refresh(s)
        bg.add_task(run_scan_job, s.id)
        return ScanOut.from_model(s)

@router.get("/scans", response_model=List[ScanOut])
def list_scans():
    with SessionLocal() as db:
        rows = db.execute(select(Scan).order_by(Scan.id.desc()).limit(200)).scalars().all()
        return [ScanOut.from_model(r) for r in rows]

@router.get("/scans/{scan_id}", response_model=ScanOut)
def get_scan(scan_id: int):
    with SessionLocal() as db:
        s = db.get(Scan, scan_id)
        if not s:
            raise HTTPException(status_code=404, detail="Scan not found")
        return ScanOut.from_model(s)

@router.delete("/scans/{scan_id}", status_code=204)
def delete_scan(scan_id: int):
    with SessionLocal() as db:
        s = db.get(Scan, scan_id)
        if not s:
            raise HTTPException(status_code=404, detail="Scan not found")
        db.delete(s)
        db.commit()
        return

@router.delete("/scans", status_code=204)
def clear_scans(status: Optional[str] = Query(default="done", description="done|error|running|all")):
    """Delete scans by status (default: done). Use status=all to wipe all."""
    with SessionLocal() as db:
        stmt = delete(Scan)
        if status in {"done","error","running"}:
            stmt = stmt.where(Scan.status == status)
        elif status == "all":
            pass
        else:
            # default behavior: clear 'done'
            stmt = stmt.where(Scan.status == "done")
        db.execute(stmt)
        db.commit()
        return
