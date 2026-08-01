FROM python:3.11-slim

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install CPU-only torch first (avoids downloading 2GB CUDA version)
RUN pip install --no-cache-dir \
    torch==2.1.0+cpu \
    torch_geometric==2.4.0 \
    --index-url https://download.pytorch.org/whl/cpu

# Install remaining production dependencies
COPY requirements-prod.txt .
RUN pip install --no-cache-dir -r requirements-prod.txt

# Install transformers (CodeBERT) - will use local cache only at runtime
RUN pip install --no-cache-dir transformers>=4.30.0

# Copy application source code
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app

# Expose backend port
EXPOSE 8000

# Start FastAPI application
CMD python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
