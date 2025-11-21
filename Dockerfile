FROM python:3.11-slim

WORKDIR /app

# Update and install runtime libraries (minimal & fast)
RUN apt-get update && apt-get install -y \
    libjpeg62-turbo \
    zlib1g \
    libfreetype6 \
    libssl-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt requirements.txt

# Install python deps (fast because ARM64 wheels exist)
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
