# Stage 1: Build dependencies
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Create non-root user
RUN groupadd -r agilegraph && useradd -r -g agilegraph agilegraph \
    && mkdir -p /app/data /app/uploads \
    && chown -R agilegraph:agilegraph /app

# Copy dependencies from builder
COPY --from=builder /root/.local /home/agilegraph/.local
ENV PATH=/home/agilegraph/.local/bin:$PATH

# Copy application source code
COPY --chown=agilegraph:agilegraph . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app

# Switch to non-root user
USER agilegraph

# Expose backend port
EXPOSE 8000

# Start FastAPI application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
