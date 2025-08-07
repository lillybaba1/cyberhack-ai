from fastapi import APIRouter, Query
router = APIRouter()

@router.get("/vuln")
def scan_vuln(target: str = Query(..., min_length=1)):
    # TODO: integrate sandboxed executor
    return {"target": target, "result": "mock"}
