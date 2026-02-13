FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for Playwright Chromium on Debian Trixie
# Note: python:3.11-slim is Debian-based, NOT Ubuntu
# We install all Chromium deps manually to avoid the --with-deps flag
# which tries to install Ubuntu-specific packages that don't exist in Debian
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    wget \
    gnupg \
    # Chromium browser dependencies
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
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxext6 \
    libdbus-1-3 \
    libexpat1 \
    libfontconfig1 \
    libgcc-s1 \
    libglib2.0-0 \
    libgtk-3-0 \
    libstdc++6 \
    libx11-6 \
    libxcb1 \
    libxext6 \
    libxi6 \
    libxtst6 \
    # Font packages (Debian equivalents of Ubuntu font packages)
    fonts-liberation \
    fonts-noto-color-emoji \
    fonts-unifont \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Set Playwright environment variables BEFORE installing browsers
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
ENV PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=0

# Install Playwright Chromium browser WITHOUT --with-deps
# All system dependencies are already installed above
RUN playwright install chromium && \
    echo "Playwright Chromium installed at $PLAYWRIGHT_BROWSERS_PATH" && \
    ls -la $PLAYWRIGHT_BROWSERS_PATH/

# Copy application code
COPY . .

# Create temp directories for file generation and sandbox
RUN mkdir -p /tmp/mcleuker_outputs /tmp/mcleuker_sandbox /tmp/mcleuker_uploads /tmp/mcleuker_files

# Expose port (Railway assigns dynamic PORT)
EXPOSE ${PORT:-8000}

# Run the backend
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
