# Qdrant Dashboard - Production Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies with increased timeout
RUN pip install --no-cache-dir --timeout=1000 -r requirements.txt

# Copy application files
COPY . .

# Create necessary directories
RUN mkdir -p /app/data

# Make init script executable
RUN chmod +x init.sh

# Expose port (Railway will set PORT env variable)
EXPOSE 8081

# Health check (using PORT env variable)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8081}/api/health || exit 1

# Run initialization and start application
CMD ["sh", "-c", "./init.sh && python app.py"]
