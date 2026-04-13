# Use the official Python 3.11 base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the entire project context into the container
COPY . .

# Install the Python dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port that Cloud Run will use
EXPOSE 8080

# The command to run the Streamlit app when the container starts.
# This correctly uses the $PORT from Cloud Run and increases the upload size.
CMD exec streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.maxUploadSize=2048
