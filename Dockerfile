# Use the official Python 3.11 base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt ./

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code (app.py, knowledge_base folder, etc.)
COPY . .

# Expose the port that Streamlit runs on (this is for documentation, not enforcement)
EXPOSE 8080

# Set a health check to ensure the app is running
# It now dynamically checks the $PORT variable
HEALTHCHECK CMD curl --fail http://localhost:${PORT}/_stcore/health

# The command to run the Streamlit app when the container starts
# We now use the $PORT environment variable provided by Cloud Run
CMD streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.maxUploadSize=2048
