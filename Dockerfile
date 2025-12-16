FROM python:3.11-slim

# Install OS dependencies + create non-root user in ONE RUN instruction
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git \
        libfreetype6 \
        libjpeg62-turbo \
        libssl-dev \
        zlib1g && \
    useradd -m appuser && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Switch to non-root user
USER appuser

# Set the working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies (as non-root via --user)
RUN pip install --no-cache-dir --user --upgrade pip setuptools wheel \
    && pip install --no-cache-dir --user -r requirements.txt

# Ensure Python can find user bin
ENV PATH="/home/appuser/.local/bin:${PATH}"

# Copy the actual application
COPY app/ ./app/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
