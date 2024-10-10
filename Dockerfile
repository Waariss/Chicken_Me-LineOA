# Use a specific version of Python slim image
FROM python:3.10.13-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*  # Clean up to reduce image size

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application files
COPY . .

# Set environment variables for configurations
ENV YOLO_CONFIG_DIR=/tmp/yolo
ENV MPLCONFIGDIR=/tmp/matplotlib

# Set the default command for the container to use gunicorn with the app
CMD ["gunicorn", "line_up_fix:app", "--bind", "0.0.0.0:8000", "--workers", "1", "--timeout", "240"]

# Expose the port the app runs on
EXPOSE 8000

