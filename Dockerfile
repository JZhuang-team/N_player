# Start from the official Python base image
FROM python:3.8

# Set environment varaibles
ENV FLASK_APP=N_layerapp.py

# Set the working directory in the container to /app
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory's contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
ENV FLASK_APP=N_layerapp

# Expose port 5000 (Flask default in this example)
EXPOSE 5000

# Use the Flask CLI with a fixed port
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
