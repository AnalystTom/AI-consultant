# Streamlit Dockerfile
FROM python:3.10-slim


# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the Streamlit app code into the container
COPY . .

# Expose the port that Streamlit uses
EXPOSE 8501

# Command to run the Streamlit app
CMD ["streamlit", "run", "streamlit_test.py", "--server.port=8501", "--server.address=0.0.0.0"]
