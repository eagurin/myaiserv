FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install poetry
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && poetry config virtualenvs.create false

# Copy poetry configuration
COPY pyproject.toml poetry.lock* ./

# Install dependencies with optimizations
RUN poetry install --no-interaction --no-ansi --no-root --no-dev

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs

# Expose ports
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]


