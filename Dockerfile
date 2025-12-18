# CryptoSentinel Dockerfile - Multi-stage build for Hugging Face Spaces

# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_SERVER_PORT=7860
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Install minimal runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy application code (selective to reduce image size)
COPY app/ app/
COPY pages/ pages/
COPY pipelines/ pipelines/
COPY storage/ storage/
COPY .streamlit/ .streamlit/
COPY dashboard.py .
COPY README_HF.md README.md

# Create directories with proper permissions
RUN mkdir -p models/active models/saved data reports && \
    chmod -R 777 models data reports

# Expose Hugging Face Spaces port
EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl --fail http://localhost:7860/_stcore/health || exit 1

# Run Streamlit on Hugging Face port
CMD ["streamlit", "run", "dashboard.py", "--server.port=7860", "--server.address=0.0.0.0"]
