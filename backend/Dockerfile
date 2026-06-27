FROM python:3.11-slim

RUN apt-get update && apt-get install -y cron && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /var/run/crond && chown appuser:appuser /var/run/crond
RUN echo "0 0 * * 1 python -m app.db.scraper" > /etc/cron.d/content-cron
RUN chmod 0644 /etc/cron.d/content-cron
RUN crontab /etc/cron.d/content-cron

RUN adduser --disabled-password --gecos "" appuser
RUN chown -R appuser:appuser /app

USER appuser

CMD ["sh", "-c", "cron -f & uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1 --loop uvloop --http httptools"]