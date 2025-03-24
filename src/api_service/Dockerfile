FROM python:3.8-slim

# Install necessary system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    curl \
    && apt-get clean

# Set up user and working directory
RUN useradd -ms /bin/bash app
USER app
WORKDIR /app

# Install pipenv
USER root
RUN pip install pipenv

# Copy Pipfile and install dependencies
COPY Pipfile Pipfile.lock ./
RUN pipenv install --system --deploy

# Copy application files
COPY main.py ./
COPY templates/ ./templates/
COPY static/ ./static/
COPY instance/ ./instance/

# Expose port and define entrypoint
EXPOSE 5000
CMD ["python", "main.py"]
