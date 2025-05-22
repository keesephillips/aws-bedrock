# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

# Make port 8080 available to the world outside this container
# App Runner will use the PORT environment variable.
# EXPOSE 8080 # Not strictly necessary if PORT env var is used by the app

# Define environment variable (though App Runner will also set this)
ENV PORT 8080

# Run app.py when the container launches
CMD ["python", "app.py"]