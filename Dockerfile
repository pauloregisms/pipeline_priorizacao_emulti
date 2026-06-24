FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "scripts/run_pipeline.py", "--config", "config/base.yaml", "--run-id", "baseline"]
