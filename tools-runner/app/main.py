import re, json, subprocess, shlex, xml.etree.ElementTree as ET
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# VERY IMPORTANT: allow-list tools + sanitize target.
ALLOWED_TOOLS = {"nmap", "whatweb"}  # extend carefully
TARGET_RE = re.compile(r"^([a-zA-Z0-9\-\.]+|\d{1,3}(\.\d{1,3}){3})$")  # basic domain/IP

class RunReq(BaseModel):
    tool: str = Field(..., examples=["nmap"])
    target: str

app = FastAPI(title="CyberHack Tools Runner")

def run(cmd: List[str], timeout: int = 60) -> Dict[str, Any]:
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return {
            "returncode": p.returncode,
            "stdout": p.stdout,
            "stderr": p.stderr,
        }
    except subprocess.TimeoutExpired:
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
    tool = req.tool.lower().strip()
    target = req.target.strip()

    if tool not in ALLOWED_TOOLS:
        raise HTTPException(400, detail="tool not allowed")
    if not TARGET_RE.match(target):
        raise HTTPException(400, detail="invalid target (only domain or IP)")

    if tool == "nmap":
        # fixed, safe-ish command; no user flags get through
        cmd = ["nmap","-sV","-Pn","--top-ports","100","-oX","-","--", target]
        res = run(cmd, timeout=90)
        parsed = parse_nmap_xml(res["stdout"])
        return {"ok": res["returncode"] == 0, "tool": "nmap", "parsed": parsed, "stderr": res["stderr"][:2000]}
    elif tool == "whatweb":
        # whatweb is often installed in pentest distros; if missing, return error
        cmd = ["whatweb","--color=never","--log-json","-","--", target]
        res = run(cmd, timeout=45)
        # best-effort parse: each line is JSON
        parsed = []
        for line in res["stdout"].splitlines():
            try:
                parsed.append(json.loads(line))
            except Exception:
                pass
        return {"ok": res["returncode"] == 0, "tool": "whatweb", "parsed": parsed[:50], "stderr": res["stderr"][:2000]}

    raise HTTPException(400, detail="unsupported tool")
