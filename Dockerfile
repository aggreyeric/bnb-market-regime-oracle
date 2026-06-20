# Market Regime Oracle — container image
# Python 3.11 slim, headless matplotlib (Agg), MCP server ready.
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    MPLBACKEND=Agg \
    PYTHONPATH=/app/src

WORKDIR /app

# Install dependencies first (better layer caching)
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the project
COPY . .

# The pipeline writes charts/CSVs/JSON to /app/results and caches raw API JSON
# under /app/data_cache. Mount a host volume over /app/results to persist artifacts.
RUN mkdir -p /app/results /app/data_cache

# Default: run the full pipeline (fetch -> classify -> backtest -> charts).
CMD ["python", "main.py"]
