# Lightweight, production-focused container for Streamlit app.
FROM python:3.11-slim

# Avoid buffering and set a working directory
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Install OS packages required for common Python packages and for image handling (Pillow/OpenCV)
RUN apt-get update && apt-get install -y \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Default port Cloud Run expects
ENV PORT=8080
EXPOSE 8080

# Run Streamlit
CMD ["streamlit", "run", "app/app.py", "--server.port=8080", "--server.address=0.0.0.0", "--server.headless=true"]