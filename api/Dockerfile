# Use Python base image
FROM python:3.9-slim

RUN mkdir /logs
RUN chmod 755 /logs
# Set working directory
WORKDIR /app

# Copy application files
COPY app.py requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update -y
RUN apt install vim -y
# Expose the application port
EXPOSE 5005

# Run the app with Gunicorn
CMD ["gunicorn", "-w", "3", "-b", "0.0.0.0:5005", "app:app"]

