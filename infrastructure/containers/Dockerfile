FROM python:3.9-slim

LABEL maintainer="QuantumUI Team <quantumui@example.com>"
LABEL description="Quantum UI Development Environment"
LABEL version="1.0.0"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    libffi-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create and activate virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Install quantum-specific packages
RUN pip install qiskit~=0.39.0 \
    qiskit-aer~=0.11.0 \
    qiskit-ibmq-provider~=0.19.0 \
    matplotlib~=3.5.2 \
    networkx~=2.8.4 \
    pylatexenc~=2.10 \
    gradio~=3.0.0

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 quantum
RUN chown -R quantum:quantum /app
USER quantum

# Expose port for Gradio
EXPOSE 7860

# Set entrypoint
ENTRYPOINT ["python", "src/main.py"]