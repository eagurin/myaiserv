set dotenv-load := false

# Install dependencies and dev tools
install:
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    pip install black==24.2.0 isort==5.13.2 flake8==7.0.0 mypy==1.8.0 ruff==0.3.0

# Format code
fmt:
    isort app
    black app
    ruff format app

# Run all linters
lint: fmt
    flake8 app
    mypy app
    ruff check app

# Run the application
run:
    uvicorn app.main:app --reload

# Run tests
test:
    pytest

# Run tests with coverage
test-cov:
    pytest --cov=app --cov-report=term-missing --cov-fail-under=80

# Run migrations
migrate:
    python scripts/manage_storage.py migrate --direction up

# Rollback migrations
rollback:
    python scripts/manage_storage.py migrate --direction down

# Check database connections
check-db:
    python scripts/manage_storage.py check

# Clear Redis cache
clear-cache:
    python scripts/manage_storage.py clear_cache

# Build the docker image
build-docker:
    docker compose build

# Start the docker containers
up-docker:
    docker compose up -d

# Stop the docker containers
down-docker:
    docker compose down -v

# Run the application in docker
run-docker:
    docker compose up -d --build
