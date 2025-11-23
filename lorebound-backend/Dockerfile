# Use Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VENV_IN_PROJECT=true \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Poetry is configured via ENV above to create venv in project directory

# Create non-root user first
RUN useradd --create-home --shell /bin/bash app

# Copy dependency files
COPY --chown=app:app pyproject.toml ./

# Copy project files
COPY . /app

# Make sure app user owns all files
RUN chown -R app:app /app

# Now switch to app user
USER app

RUN poetry install --only=main --no-root

# Switch to app user and install dependencies (creates venv in .venv)
USER app
RUN poetry install --only=main --no-root

# Copy application code as app user
USER root
COPY --chown=app:app app/ ./app/
COPY --chown=app:app migrations/ ./migrations/
COPY --chown=app:app scripts/ ./scripts/
COPY --chown=app:app alembic.ini ./

# Switch back to app user
USER app

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
