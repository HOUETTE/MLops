#!/bin/sh
# Startup script for Spam Detector API
# Handles PORT environment variable for App Runner compatibility

# Use PORT environment variable if set, otherwise default to 8000
PORT=${PORT:-8000}

echo "Starting Spam Detector API on port ${PORT}..."

# Start uvicorn with the configured port
exec uvicorn src.api.main:app --host 0.0.0.0 --port ${PORT}
