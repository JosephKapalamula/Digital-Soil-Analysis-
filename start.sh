#!/bin/bash

# Ensure gunicorn is available and run the application
python -m gunicorn -w 1 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
