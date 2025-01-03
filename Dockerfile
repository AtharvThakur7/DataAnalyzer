# filepath: /C:/Users/athar/DataAnalyzer/Dockerfile
# Use the official Python image from the Docker Hub
# FROM python:3.9-slim
FROM python:3.11.4-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files
COPY . /app/

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose the port the app runs on
EXPOSE 8000

# Run the application
CMD ["gunicorn", "DataAnalyzer.wsgi:application", "--bind", "0.0.0.0:8000"]