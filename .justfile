# Define tasks for managing the project

# Install dependencies
install:
  pip install -r requirements.txt

# Run the application
run:
  uvicorn app.main:app --reload

# Run tests
test:
  pytest

# Run tests with coverage
test-cov:
  pytest --cov=app

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

# Lint the code
lint:
  pylint app tests