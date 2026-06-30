FROM python:3.11-slim

LABEL name="archivebox" \
    maintainer="Nick Sweeting <dockerfile@archivebox.io>" \
    description="All-in-one self-hosted internet archiving solution" \
    homepage="https://github.com/ArchiveBox/ArchiveBox"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    wget \
    git \
    dnsutils \
    iputils-ping \
    tree \
    nano \
    && rm -rf /var/lib/apt/lists/*

# Create archivebox user
RUN useradd -m -s /bin/bash archivebox

# Set up working directory
WORKDIR /data

# Install ArchiveBox from PyPI
RUN pip install --no-cache-dir archivebox

# Fix permissions
RUN chown -R archivebox:archivebox /data && chmod 755 /data

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Switch to non-root user
USER archivebox

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
