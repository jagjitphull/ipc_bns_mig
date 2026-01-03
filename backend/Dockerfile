FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Create directories for database and vector store
RUN mkdir -p /app/data /app/chroma_db

# Expose port
EXPOSE 8000

# Run database initialization and start server
CMD ["sh", "-c", "cd app && python init_db.py && python -m uvicorn main:app --host 0.0.0.0 --port 8000"]
