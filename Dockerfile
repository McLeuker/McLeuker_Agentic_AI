# McLeuker Fashion AI Platform V3.1
# Dockerfile for Railway deployment
# Cache bust: 2026-02-01-v3.1.0-killer

FROM python:3.11-slim

LABEL version="3.1.0"
LABEL description="McLeuker Fashion AI Platform - Frontier Agentic AI"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create output directories
RUN mkdir -p /tmp/outputs /tmp/temp

# Set output directories
ENV OUTPUT_DIR=/tmp/outputs
ENV TEMP_DIR=/tmp/temp

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
