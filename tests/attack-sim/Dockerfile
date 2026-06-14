FROM python:3.11-slim
RUN apt-get update -qq && apt-get install -y -q gcc git make libc6-dev --no-install-recommends \
    && pip install --no-cache-dir gmssl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*
WORKDIR /work
