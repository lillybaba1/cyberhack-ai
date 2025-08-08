import os, subprocess

DRY_RUN = os.getenv("DRY_RUN") == "1"

def run_cmd(cmd, timeout=60):
    if DRY_RUN:
        return subprocess.CompletedProcess(cmd, 0, stdout="{}", stderr="")
    return run_cmd(cmd, capture_output=True, text=True, timeout=timeout)

import re, json, subprocess, sys, xml.etree.ElementTree as ET
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

ALLOWED_TOOLS = {"nmap","whatweb","sqlmap","dirb","dnsenum","curl"}  # keep in sync with Dockerfile
# Accept bare host/IP or full URL; capture host/IP in group(1)
TARGET_RE = re.compile(r"^(?:https?://)?([a-zA-Z0-9\.-]+|\d{1,3}(?:\.\d{1,3}){3})(?:/.*)?$")

class RunReq(BaseModel):
    tool: str = Field(..., examples=["nmap"])
    target: str

app = FastAPI(title="CyberHack Tools Runner")

def log(msg: str) -> None:
    print(msg, file=sys.stdout, flush=True)

def normalize(raw: str) -> tuple[str,str,str]:
    """
    Returns (host, proto, full_url). Host is bare (no scheme/path).
    """
    raw = (raw or "").strip()
    m = re.match(r'^(https?://)?([^/?#]+)(.*)$', raw)
    if not m:
        raise HTTPException(400, detail="invalid target format")
    proto = m.group(1) or "http://"
    host  = m.group(2)
    path  = m.group(3) or "/"
    if not TARGET_RE.match(host):
        raise HTTPException(400, detail="invalid host (domain or IPv4)")
    return host, proto.rstrip(":/"), f"{proto}{host}{path}"

def sh(cmd: List[str], timeout: int = 180) -> Dict[str, Any]:
    log(f"[runner] Running: {' '.join(cmd)}")
    try:
        p = run_cmd(cmd, capture_output=True, text=True, timeout=timeout)
        if p.stdout: log(f"[runner] stdout ({len(p.stdout)}):\n{p.stdout[:4000]}")
        if p.stderr: log(f"[runner] stderr ({len(p.stderr)}):\n{p.stderr[:2000]}")
        return {"code": p.returncode, "out": p.stdout, "err": p.stderr}
    except subprocess.TimeoutExpired:
        log("[runner] ERROR: timeout")
        raise HTTPException(408, detail="tool timeout")

def parse_nmap_xml(xml_text: str) -> Dict[str, Any]:
    out = {"open_ports": []}
    try:
        root = ET.fromstring(xml_text)
        for host in root.findall(".//host"):
            for port in host.findall(".//port"):
                state = port.find("state")
                if state is not None and state.get("state") == "open":
                    svc = port.find("service")
                    out["open_ports"].append({
                        "port": int(port.get("portid", "0")),
                        "proto": port.get("protocol", ""),
                        "service": (svc.get("name") if svc is not None else None),
                        "product": (svc.get("product") if svc is not None else None),
                        "version": (svc.get("version") if svc is not None else None),
                    })
    except Exception:
        pass
    return out

@app.post("/run")
def run_tool(req: RunReq):
    tool = (req.tool or "").lower().strip()
    if tool not in ALLOWED_TOOLS:
        raise HTTPException(400, detail="tool not allowed")

    host, proto, full_url = normalize(req.target)

    if tool == "nmap":
        # Fast-ish scan; bail after 30s per host to avoid hangs
        res = sh([
            "nmap","-sV","-Pn","--top-ports","100",
            "--host-timeout","30s",
            "-oX","-","--", host
        ], timeout=150)
        return {"tool":"nmap","ok":res["code"]==0,
                "parsed":parse_nmap_xml(res["out"]),
                "stdout":res["out"][-4000:], "stderr":res["err"][:2000]}

    if tool == "whatweb":
        res = sh(["whatweb","--color=never","--log-json","-","--", full_url], timeout=60)
        lines=[]; 
        for line in res["out"].splitlines():
            try: lines.append(json.loads(line))
            except: pass
        return {"tool":"whatweb","ok":res["code"]==0,
                "parsed":lines[:50],"stdout":res["out"][-4000:], "stderr":res["err"][:2000]}

    if tool == "sqlmap":
        # Keep safe defaults; force http to avoid SSL prompts
        res = sh(["sqlmap","-u", f"http://{host}","--batch","--crawl=0"], timeout=300)
        return {"tool":"sqlmap","ok":res["code"]==0,
                "stdout":res["out"][-4000:], "stderr":res["err"][:2000]}

    if tool == "dirb":
        res = sh(["dirb", f"http://{host}", "/usr/share/dirb/wordlists/common.txt","-S","-o","-"], timeout=300)
        return {"tool":"dirb","ok":res["code"]==0,
                "stdout":res["out"][-4000:], "stderr":res["err"][:2000]}

    if tool == "dnsenum":
        res = sh(["dnsenum", host], timeout=150)
        return {"tool":"dnsenum","ok":res["code"]==0,
                "stdout":res["out"][-4000:], "stderr":res["err"][:2000]}

    if tool == "curl":
        res = sh(["curl","-fsSIL", full_url], timeout=30)
        return {"tool":"curl","ok":res["code"]==0,
                "headers":res["out"], "stdout":res["out"][-4000:], "stderr":res["err"][:2000]}

    raise HTTPException(400, detail="unsupported tool")
