# 1. Base Image
FROM python:3.11-slim

# 2. System Dependencies
RUN apt-get update && apt-get install -y cron && rm -rf /var/lib/apt/lists/*

# 3. Working Directory
WORKDIR /app

# 4. Copy Dependencies
# If the file is in the same folder as the Dockerfile, this should work.
# If it still fails, use the explicit path:
COPY requirements.txt ./
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

# 8. Start Service
CMD ["sh", "-c", "cron -f & uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1 --loop uvloop --http httptools"]