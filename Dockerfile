# Build environment for creating Linux binaries
# Uses older glibc (2.31) for broader compatibility
FROM python:3.11-bullseye

WORKDIR /app

# Install build dependencies
RUN apt-get update && \
    apt-get install -y binutils && \
    rm -rf /var/lib/apt/lists/* && \
    pip install uv
