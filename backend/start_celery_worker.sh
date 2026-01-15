#!/bin/bash
# Start Celery Worker for Interview Question Generation

export PYTHONPATH="${PYTHONPATH}:$(pwd)"

celery -A app.core.celery_app worker \
  --loglevel=info \
  --concurrency=2 \
  --max-tasks-per-child=10 \
  --task-events \
  --without-gossip \
  --without-mingle \
  --without-heartbeat
