FROM python:3.10-slim

# Install system dependencies for Scapy and compilation
RUN apt-get update && apt-get install -y \
    libpcap-dev \
    gcc \
    iproute2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY core/ core/
COPY web/ web/

# Create models directory
RUN mkdir models

# Set Python path
ENV PYTHONPATH=/app

# Default command (overridden by compose)
CMD ["python", "-m", "core.main"]
