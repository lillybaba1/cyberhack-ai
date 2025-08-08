FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "-c", "from scanner import calculate_risk; print(calculate_risk(10))"]  # Test on build