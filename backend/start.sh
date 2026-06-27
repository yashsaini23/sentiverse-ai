#!/bin/sh
# Start cron in the background
cron -f &
# Start the main application
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1 --loop uvloop --http httptools