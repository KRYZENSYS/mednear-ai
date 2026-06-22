# ============================================
# MedNear AI - Production Dockerfile
# ============================================

FROM python:3.12-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    gcc \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM base AS production

RUN groupadd -r mednear && useradd -r -g mednear mednear

COPY . /app

RUN mkdir -p /app/logs /app/uploads /app/temp && \
    chown -R mednear:mednear /app

USER mednear

EXPOSE 8443 9090

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:9090/health || exit 1

CMD ["python", "-m", "bot.main"]