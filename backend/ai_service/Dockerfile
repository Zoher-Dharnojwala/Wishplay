# Use a small Linux image with Python 3.10
FROM python:3.10-slim

# Set working directory inside container
WORKDIR /app

# Copy dependency list and install
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the rest of your code
COPY . .

# Expose the Flask port
EXPOSE 6000

# Start the Flask API when the container runs
CMD ["python", "api.py"]
