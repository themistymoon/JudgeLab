# Secure C++ execution environment for judging  
FROM gcc:13

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
CMD ["g++"]