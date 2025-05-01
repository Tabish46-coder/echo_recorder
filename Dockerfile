# Start from a Python 3.11 image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Install ffmpeg
RUN apt-get update && apt-get install -y ffmpeg

# Copy the application code into the container
COPY . /app/

# Expose port (default for Flask)
EXPOSE 5000

# Run the app
CMD ["python", "run.py"]
