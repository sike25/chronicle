# Chronicle Dockerfile
# Target: Google Cloud Platform Cloud Run (linux/amd64)

# lean image, no build tools needed.
FROM python:3.11-slim

# for cloud run logs
ENV PYTHONUNBUFFERE=1 \
PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# --- Dependencies ---

# reruns only when requirements.txt changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# -- Application Code --
COPY . .

# create logs directory
RUN mkdir -p /app/logs

# -- Non-root User ---

RUN adduser --disabled-password -gecos "" chronicle
RUN chown -R chronicle:chronicle /app
USER chronicle

# keeps SSE connection alive for up to ~10 minutes.
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT:-8080} --timeout-keep-alive 620"]

