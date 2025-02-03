FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install dependencies with optimizations
RUN pip install --upgrade pip \
    && pip install --force-reinstall Cython \
    && pip install --no-cache-dir -r requirements.txt \
    && rm -rf /root/.cache/pip/*


# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs

# Expose ports
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]


