FROM python:3.12-slim

# Install system dependencies for C++ extensions (numpy, pandas, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install via uv
COPY requirements.txt .
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
RUN uv pip install --system --no-cache-dir \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    -r requirements.txt

# Ensure gunicorn is available as a command
RUN python -m pip install --no-cache-dir gunicorn==23.0.0

# Copy the rest of the application
COPY . .

# Make start script executable
RUN chmod +x start.sh

# Set the environment variable so imports look in the /app root
ENV PYTHONPATH=/app

EXPOSE 8000

# Use the start script
CMD ["./start.sh"]