# FastAPI Dockerfile
FROM python:3.10-slim


# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the FastAPI app code into the container
COPY . .

# Expose the FastAPI default port
EXPOSE 8000

# Command to run the FastAPI app
CMD ["uvicorn", "idea_analysis:app", "--host", "0.0.0.0", "--port", "8000"]
