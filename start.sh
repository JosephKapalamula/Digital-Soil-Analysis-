#!/bin/bash

echo "Starting Digital Soil Analysis Backend..."
echo "Python version: $(python --version)"
echo "Current directory: $(pwd)"
echo "Environment variables:"
env | grep -E "(PORT|PYTHONPATH|DATABASE_URL)" || echo "No PORT/PYTHONPATH/DATABASE_URL found"

# Use Render's PORT if available, otherwise default to 8000
PORT=${PORT:-8000}
echo "Using PORT: $PORT"

echo "Files in current directory:"
ls -la

# Check if app directory exists
if [ ! -d "app" ]; then
    echo "ERROR: app directory not found!"
    exit 1
fi

echo "Testing Python imports..."
python -c "import app.main; print('✅ app.main imported successfully')" || echo "❌ Failed to import app.main"

echo "Starting gunicorn with uvicorn worker on port $PORT..."
python -m gunicorn -w 1 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:$PORT --timeout 120 --keep-alive 2 --max-requests 1000 --max-requests-jitter 100 --access-logfile - --error-logfile - --log-level debug
