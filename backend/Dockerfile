# Stage 1: Build dependencies
FROM python:3.11-slim as builder
WORKDIR /app
RUN apt-get update && apt-get install -y build-essential curl
RUN pip install uv
COPY requirements.txt .
RUN uv pip install --system --no-cache -r requirements.txt

# Stage 2: Production Image
FROM python:3.11-slim

# --- ROOT TASKS START HERE ---
WORKDIR /app

# Install cron and other system dependencies as root
RUN apt-get update && apt-get install -y cron && rm -rf /var/lib/apt/lists/*

# Add the cron job
RUN echo "0 0 * * 1 python -m app.db.scraper" > /etc/cron.d/content-cron
RUN chmod 0644 /etc/cron.d/content-cron

# Create non-root user
RUN adduser --disabled-password --gecos "" appuser

# Copy dependencies and files
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY ./app /app/app

# Set permissions
RUN mkdir -p /app/chroma_data && chown -R appuser:appuser /app

# Switch to the non-root user
USER appuser
# --- ROOT TASKS END ---

EXPOSE 8000

# Start cron AND uvicorn
CMD ["sh", "-c", "sudo cron && uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4"]
