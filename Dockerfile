# ============================================
# Stage 1: Build Stage
# ============================================
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt \
    && python -m nltk.downloader punkt stopwords averaged_perceptron_tagger -d /opt/nltk_data

# ============================================
# Stage 2: Runtime Stage
# ============================================
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    FLASK_APP=app.py \
    FLASK_ENV=production \
    NLTK_DATA=/opt/nltk_data \
    HOME=/home/appuser

WORKDIR /app

# Copy venv and nltk data
COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /opt/nltk_data /opt/nltk_data

# Create real user WITH HOME DIRECTORY
RUN useradd -m -s /bin/bash appuser

# Copy application
COPY . .

# Fix ownership
RUN chown -R appuser:appuser /app /opt/nltk_data /home/appuser

USER appuser

EXPOSE 5000

CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]
