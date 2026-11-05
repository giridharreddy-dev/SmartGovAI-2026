FROM node:24-bookworm-slim AS frontend
WORKDIR /build
COPY frontend/package*.json ./
RUN npm ci --no-audit --no-fund
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-tel \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

COPY . .
COPY --from=frontend /build/dist ./frontend/dist

RUN groupadd --system smartgov && useradd --system --gid smartgov smartgov \
    && mkdir -p uploads static/audio/dynamic /var/lib/smartgov \
    && chown -R smartgov:smartgov uploads static/audio/dynamic /var/lib/smartgov

ENV DB_PATH=/var/lib/smartgov/feedback.db
USER smartgov

EXPOSE 5000

CMD ["sh", "-c", "exec gunicorn --bind 0.0.0.0:${PORT:-5000} --worker-class gthread --workers 2 --threads 4 --timeout 90 --access-logfile - app:app"]
