FROM python:3.12-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --target=/deps -r requirements.txt

FROM python:3.12-slim

# SECURITY: Create non-root user
RUN adduser --disabled-password --gecos '' appuser

WORKDIR /app

# Copy only deps from builder (no pip cache, no build tools)
COPY --from=builder /deps /usr/local/lib/python3.12/site-packages/

COPY . .

# Ensure data directory is writable
RUN mkdir -p /app/data && chown -R appuser:appuser /app

USER appuser

# Lightweight healthcheck (no extra process)
HEALTHCHECK --interval=120s --timeout=3s --retries=2 \
    CMD python -c "import os,sys; sys.exit(0 if os.path.exists('/app/data/worker_start_epoch.txt') else 1)"

CMD ["python", "-u", "worker.py"]
