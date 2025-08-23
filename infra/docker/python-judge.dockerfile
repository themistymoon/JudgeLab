# Secure Python execution environment for judging
FROM python:3.12-slim

# Create non-root user
RUN groupadd -r judge && useradd -r -g judge judge

# Install basic utilities
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    time \
    && rm -rf /var/lib/apt/lists/*

# Create execution directory
RUN mkdir -p /judge && chown judge:judge /judge

# Switch to non-root user
USER judge
WORKDIR /judge

# Default command
CMD ["python3"]