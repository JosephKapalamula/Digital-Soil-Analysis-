#!/bin/bash

echo "Starting Digital Soil Analysis Backend..."
echo "Python version: $(python --version)"
echo "Current directory: $(pwd)"
echo "Files in current directory:"
ls -la

# Check if app directory exists
if [ ! -d "app" ]; then
    echo "ERROR: app directory not found!"
    exit 1
fi

echo "Starting gunicorn with uvicorn worker..."
python -m gunicorn -w 1 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000 --timeout 120 --keep-alive 2 --max-requests 1000 --max-requests-jitter 100
