# Dockerfile for the HR Attrition Prediction API
# Dockerfile

# Python Base image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy requirements.txt and install Python dependencies
COPY . .
# Install system deps (curl for HEALTHCHECK) and then Python deps
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        postgresql-client \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy your FastAPI application code (the 'app' directory)



RUN chmod +x /app/app/entrypoint.sh
ENTRYPOINT ["/app/app/entrypoint.sh"]

# Expose the port FastAPI will run on
EXPOSE 8000

# Basic healthcheck to ensure the container is responsive
HEALTHCHECK --interval=30s --timeout=3s --retries=3 CMD curl -f http://localhost:8000/health || exit 1

# 7. Command to run the application when the container starts
#    'app.main:app' refers to the 'app' FastAPI instance in 'app/main.py'
#    --workers: Adjust based on CPU cores (e.g., 2-4 workers per CPU core is a common starting point)
#    --worker-class: Tells Gunicorn to use Uvicorn's worker class for FastAPI
#    --bind: Listens on all network interfaces on port 8000
CMD ["gunicorn", "app.main:app", "--workers", "2", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]