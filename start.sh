#!/bin/sh
# Startup script for Spam Detector API + Streamlit UI

set -e

# Use PORT environment variable if set, otherwise default to 8000
API_PORT=${PORT:-8000}
STREAMLIT_PORT=${STREAMLIT_PORT:-8501}

echo "Starting Spam Detector API on port ${API_PORT}..."
uvicorn src.api.main:app --host 0.0.0.0 --port ${API_PORT} &
API_PID=$!

cleanup() {
  kill "${API_PID}" 2>/dev/null || true
}

trap cleanup INT TERM

echo "Starting Streamlit UI on port ${STREAMLIT_PORT}..."
streamlit run /app/app.py --server.address 0.0.0.0 --server.port ${STREAMLIT_PORT}
