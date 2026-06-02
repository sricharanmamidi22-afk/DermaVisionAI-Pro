# Use Python 3.11.13 slim image to match runtime.txt and app dependencies
FROM python:3.11.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

# Ensure application root is on PYTHONPATH so imports like `import backend` work
ENV PYTHONPATH=/app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application
COPY . .

# Create uploads directory
RUN mkdir -p uploads

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=backend/app.py
ENV FLASK_ENV=production

# Run the application with Gunicorn in production
ENV PORT=5000
# Use shell form so $PORT is expanded at runtime
CMD gunicorn backend.app:app --bind 0.0.0.0:$PORT --workers 2 --preload --timeout 120