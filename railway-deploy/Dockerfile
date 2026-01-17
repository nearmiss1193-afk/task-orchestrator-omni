FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.railway.txt .
RUN pip install --no-cache-dir -r requirements.railway.txt

# Copy application
COPY railway_fallback_runner.py .

# Expose port (Railway sets PORT env var)
EXPOSE 8080

# Run the application
CMD ["python", "railway_fallback_runner.py"]
