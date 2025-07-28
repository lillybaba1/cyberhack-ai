FROM python:3-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install Python dependencies
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

# Create app directory
WORKDIR /app
COPY . /app

# Add non-root user and fix permissions
RUN adduser -u 5678 --disabled-password --gecos "" appuser \
    && chown -R appuser /app

# Install socketio
RUN python -m pip install "python-socketio[asyncio]"==5.11.2

# Install Node and global packages
RUN apt-get update && apt-get install -y nodejs npm \
    && npm install -g create-react-app \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Fix frontend permissions before switching to non-root
RUN chown -R appuser:appuser /app/frontend

# Switch to appuser AFTER setting permissions
USER appuser

# Build React app
WORKDIR /app/frontend
RUN npm install
RUN npm run build

# Ports
EXPOSE 8000
EXPOSE 3000

# Start backend (FastAPI) and frontend (React)
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port 8000 & cd /app/frontend && npm start"]
