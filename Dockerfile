FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y cron && rm -rf /var/lib/apt/lists/*

# Create app user first
RUN adduser --disabled-password --gecos "" appuser

WORKDIR /app

# Set up permissions for app folder before copying files
RUN chown -R appuser:appuser /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Setup cron (running as a standard job)
RUN echo "0 0 * * 1 python -m backend.app.db.scraper" > /etc/cron.d/content-cron
RUN chmod 0644 /etc/cron.d/content-cron
RUN crontab /etc/cron.d/content-cron

# Set ownership of the crontab file to appuser
RUN chown appuser:appuser /etc/cron.d/content-cron

# Switch to the non-root user
USER appuser

# Use PYTHONPATH to ensure 'import app' works from the backend directory
ENV PYTHONPATH=/app/backend

# Start cron in the background and uvicorn in the foreground
# Use 'cron -f' to run in foreground; we remove the PID file requirement
CMD ["sh", "-c", "cron & uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1 --loop uvloop"]