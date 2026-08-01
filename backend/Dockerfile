FROM python:3.11-slim

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install CPU-only torch (separate from PyPI packages — uses PyTorch wheel server)
RUN pip install --no-cache-dir torch==2.1.0+cpu --index-url https://download.pytorch.org/whl/cpu

# Install torch_geometric from PyPI (requires torch to be installed first)
RUN pip install --no-cache-dir torch_geometric

# Install transformers for CodeBERT (local cache only at runtime)
RUN pip install --no-cache-dir "transformers>=4.30.0"

# Install remaining production dependencies
COPY requirements-prod.txt .
RUN pip install --no-cache-dir -r requirements-prod.txt

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
