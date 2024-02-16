# Add base image
FROM python:3.12.0-slim-bookworm

# Set environment variables
ENV PYTHONBUFFERED 1
ENV PYTHONWRITEBYTECODE 1
ENV APP=/app

# Change the working directory
WORKDIR $APP

# Add requirements.txt file
COPY requirements.txt $APP

# Install and update Python
RUN pip3 install -r requirements.txt

# Copy the rest of the files
COPY . $APP

# Expose port
EXPOSE 8000

# Make the entrypoint.sh file executable
RUN chmod +x /app/entrypoint.sh

# Run command to start application
ENTRYPOINT ["/bin/bash","/app/entrypoint.sh"]
CMD ["gunicorn", "--bind", ":8000", "--workers", "3", "djangobackend.wsgi"]
