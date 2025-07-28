# Architecture Diagrams

## High-Level Overview (Text-Based ASCII)
User -> Frontend (React) -> Backend (FastAPI) -> AI Services -> Tools (Nmap, Metasploit, etc.)
                             |
                             v
                          Database (Postgres/Redis)

## Data Flow
1. User auth via OAuth2/JWT.
2. Scan request -> AI orchestrator -> Tool chain (conditional branches).
3. Results -> Dashboard (charts via Recharts).

Expand with Mermaid diagrams in future.
