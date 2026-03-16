FROM python:3.12-slim

# Prevent python from writing pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    python3-dev \
    libssl-dev \
    libffi-dev \
    curl \
    git \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install poetry
RUN pip install poetry

# Disable Poetry virtualenvs
RUN poetry config virtualenvs.create false

# Copy dependency files
COPY pyproject.toml poetry.lock /app/

# Install dependencies
RUN poetry install --no-root

# Copy project files
COPY . /app

# Make start.sh executable
RUN chmod +x /app/start.sh

# Create non-root user
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# Set permissions
RUN chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Run start script
CMD ["/app/start.sh"]