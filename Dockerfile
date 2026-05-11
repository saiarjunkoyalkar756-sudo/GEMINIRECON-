FROM python:3.11-slim

# Set non-interactive to avoid hanging on prompts
ENV DEBIAN_FRONTEND=noninteractive

# Update apt and install dependencies with a fallback for package lists
RUN apt-get update || apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    git \
    wget \
    dnsutils \
    whois \
    nmap \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt honcho

# Create a Procfile for honcho to manage both processes
RUN echo "web: uvicorn api.main:app --host 0.0.0.0 --port \$PORT" > Procfile && \
    echo "worker: celery -A workers.tasks.celery_app worker --loglevel=info --concurrency=1 --max-tasks-per-child=1" >> Procfile

CMD ["honcho", "start"]
