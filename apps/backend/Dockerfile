FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (including Playwright browser deps)
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    wget \
    gnupg \
    # Playwright Chromium dependencies
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    libatspi2.0-0 \
    libwayland-client0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
# Cache bust: V6.3 - playwright browser engine + local sandbox
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright Chromium browser
RUN playwright install chromium || echo "Playwright browser install skipped (will use system chromium)"

# Copy application code
COPY . .

# Create temp directories for file generation and sandbox
RUN mkdir -p /tmp/mcleuker_outputs /tmp/mcleuker_sandbox /tmp/mcleuker_uploads /tmp/mcleuker_files

# Expose port (Railway assigns dynamic PORT)
EXPOSE ${PORT:-8000}

# Run the Kimi 2.5 Complete Production Backend
# Use shell form so $PORT env var is expanded at runtime
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
