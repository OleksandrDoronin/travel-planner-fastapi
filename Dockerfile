# Define the base image
FROM python:3.12-slim

# Upgrade pip to the latest version
RUN pip install --upgrade pip

# Install Poetry for managing dependencies
RUN pip install poetry

# Set environment variables to prevent Python from writing .pyc files and to ensure logs are outputted in real-time
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /fastapi-app

# Copy dependency files to the working directory
COPY pyproject.toml poetry.lock /fastapi-app/

# Configure Poetry to not create a virtual environment and install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Copy the rest of the application code to the working directory
COPY . /fastapi-app

ENV PYTHONPATH=/fastapi-app/src
# Expose port 8000 to be accessible from outside the container
EXPOSE 8000

# Copy the start script to the working directory and make it executable
COPY start.sh /fastapi-app/start.sh
RUN chmod +x /fastapi-app/start.sh

# Specify the command to run the start script when the container starts
CMD ["/fastapi-app/start.sh"]


