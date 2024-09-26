# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory to /app
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install fastapi[standard]
# Copy the application code into the container
COPY . .

# Expose port 8501 for the FastAPI app to listen on
EXPOSE 8501

# Run the command to start the development server when the container is run
CMD ["fastapi", "run", "main.py", "--port=8501"]