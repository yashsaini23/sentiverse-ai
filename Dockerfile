FROM python:3.11-slim
RUN apt-get update && apt-get install -y cron && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# 1. CREATE USER FIRST
RUN adduser --disabled-password --gecos "" appuser

# 2. THEN CHANGE OWNERSHIP
RUN mkdir -p /var/run/crond && chown -R appuser:appuser /var/run/crond
RUN chown -R appuser:appuser /app

# 3. CONFIGURE CRON
RUN echo "0 0 * * 1 python -m backend.app.db.scraper" > /etc/cron.d/content-cron
RUN chmod 0644 /etc/cron.d/content-cron
RUN crontab /etc/cron.d/content-cron

# Keep all your previous RUN/COPY commands, just replace the final part:

# Ensure the backend directory is in the path so 'from app...' works
ENV PYTHONPATH=/app/backend

USER appuser

# Start cron and uvicorn correctly
# cron -f runs in the foreground
# Change --workers 1 to --workers 1 and ensure it's not a higher number
CMD ["sh", "-c", "cron & uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --workers 1 --loop uvloop"]