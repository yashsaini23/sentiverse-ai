# Stage 1: Build dependencies
FROM python:3.11-slim as builder
WORKDIR /app
RUN apt-get update && apt-get install -y build-essential curl
# Install uv for blazingly fast Python dependency resolution
RUN pip install uv
COPY requirements.txt .
RUN uv pip install --system --no-cache -r requirements.txt

# Stage 2: Production Image
FROM python:3.11-slim
WORKDIR /app
# Create non-root user
RUN adduser --disabled-password --gecos "" appuser
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY ./app /app/app
# Set permissions for Vector DB persistent volume
RUN mkdir -p /app/chroma_data && chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
# Install cron
RUN apt-get update && apt-get install -y cron

# Add the script to crontab
RUN echo "0 0 * * 1 root python -m app.db.scraper" > /etc/cron.d/content-cron
RUN chmod 0644 /etc/cron.d/content-cron
RUN crontab /etc/cron.d/content-cron

# Start cron in the background
CMD ["sh", "-c", "cron && uvicorn app.main:app --host 0.0.0.0 --port 8000"]