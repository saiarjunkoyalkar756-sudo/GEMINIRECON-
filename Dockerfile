FROM python:3.11-slim

# Set non-interactive to avoid hanging on prompts
ENV DEBIAN_FRONTEND=noninteractive

# Update apt and install dependencies with a fallback for package lists
RUN apt-get update || apt-get update &&     apt-get install -y --no-install-recommends     curl     git     wget     dnsutils     whois     nmap     && apt-get clean     && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
