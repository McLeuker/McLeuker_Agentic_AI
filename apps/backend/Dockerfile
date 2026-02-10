FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
# Cache bust: V5.5 - stripe + supabase billing
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create temp directories for file generation and sandbox
RUN mkdir -p /tmp/mcleuker_outputs /tmp/mcleuker_sandbox /tmp/mcleuker_uploads /tmp/mcleuker_files

# Expose port (Railway assigns dynamic PORT)
EXPOSE ${PORT:-8000}

# Run the Kimi 2.5 Complete Production Backend
# Use shell form so $PORT env var is expanded at runtime
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
