# Use python image
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y cron && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy everything from the backend folder to the container's /app folder
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create non-root user
RUN adduser --disabled-password --gecos "" appuser
RUN chown -R appuser:appuser /app
USER appuser

# Start the app
CMD ["sh", "-c", "cron -f & uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1"]