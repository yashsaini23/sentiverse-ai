# 1. Base Image
FROM python:3.11-slim

# 2. System Dependencies
RUN apt-get update && apt-get install -y cron && rm -rf /var/lib/apt/lists/*

# 3. Working Directory
WORKDIR /app

# Explicitly look in the backend folder
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy Application Code
COPY . .

# 6. Setup Cron Job
RUN echo "0 0 * * 1 python -m app.db.scraper" > /etc/cron.d/content-cron
RUN chmod 0644 /etc/cron.d/content-cron
RUN crontab /etc/cron.d/content-cron

# 7. Non-Root User Setup
RUN adduser --disabled-password --gecos "" appuser
RUN chown -R appuser:appuser /app
USER appuser
# Fix permissions so cron can write to its directory
RUN mkdir -p /var/run/crond && chown appuser:appuser /var/run/crond

# Create non-root user and set ownership
RUN adduser --disabled-password --gecos "" appuser
RUN chown -R appuser:appuser /app

USER appuser

# Use the absolute path to your Python module
# If your project is 'backend/app', ensure we are in the right WORKDIR
CMD ["sh", "-c", "cron -f & uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1"]
2. Fix the Module Path (The ModuleNotFoundError)