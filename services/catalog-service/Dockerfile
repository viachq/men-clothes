#syntax=docker/dockerfile:1

# === Build stage: Install dependencies ===
FROM python:3.13-slim AS builder

ENV LANG=C.UTF-8
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Create virtual environment and install dependencies
RUN python -m venv /app/venv && \
    /app/venv/bin/pip install --upgrade pip && \
    /app/venv/bin/pip install --no-cache-dir -r requirements.txt
ENV PATH="/app/venv/bin:$PATH"

# === Final stage: Runtime image ===
FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PATH="/app/venv/bin:$PATH"

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/venv /app/venv

# Copy application code
COPY backend ./backend

# Create directory for database
RUN mkdir -p /app/data

# Set PYTHONPATH to include the service directory
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8002

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8002/health')" || exit 1

# Run uvicorn
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8002"]
