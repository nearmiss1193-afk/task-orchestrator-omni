# Use official Python 3.10 slim image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set Environment Variables (Defaults, can be overridden)
ENV PYTHONUNBUFFERED=1

# Command to run the worker
CMD ["python", "worker.py"]
