FROM python:3.11-slim

WORKDIR /app

# Update and install runtime libraries (minimal & fast)
RUN apt-get update && apt-get install -y \
    libfreetype6 \
    libjpeg62-turbo \
    libssl-dev \
    zlib1g \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt requirements.txt

# Install python deps (fast because ARM64 wheels exist)
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
