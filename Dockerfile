FROM ubuntu:22.04

# Install basics
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    nodejs \
    npm \
    chromium-browser \
    xvfb \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Playwright for screenshots
RUN pip3 install playwright && playwright install chromium

# Create workspace
WORKDIR /workspace

# Keep container running
CMD ["tail", "-f", "/dev/null"]