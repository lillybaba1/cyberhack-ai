FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Only tools available in Debian slim repos
RUN apt-get update && apt-get install -y --no-install-recommends \
    nmap \
    whatweb \
    sqlmap \
    dirb \
    dnsenum \
    netcat-openbsd \
    curl \
    wget \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/*

RUN adduser --disabled-password --gecos "" appuser
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
USER appuser
EXPOSE 9000
CMD ["python","-m","uvicorn","app.main:app","--host","0.0.0.0","--port","9000"]
