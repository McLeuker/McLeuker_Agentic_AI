# McLeuker Agentic AI Platform - Docker Image
# Production-ready container for deployment

FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV PORT=8000

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
RUN mkdir -p outputs temp

# Expose port
EXPOSE 8000

# Run the application using shell form to ensure environment variables are expanded
CMD uvicorn src.api.main:app --host 0.0.0.0 --port ${PORT:-8000}
