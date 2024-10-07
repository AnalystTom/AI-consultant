# MVP Generator for your Ideas - Project Setup

This guide will help you run the Streamlit frontend and FastAPI backend for the **MVP Generator** tool. This project allows users to input information about their business needs and generates relevant AI solutions, feasibility assessments, and reports.

## Prerequisites

Ensure you have Python 3.7+ installed and have access to a terminal or command prompt.

### Dependencies

1. [Python 3.7+](https://www.python.org/downloads/)
2. [FastAPI](https://fastapi.tiangolo.com/) - Backend framework.
3. [Uvicorn](https://www.uvicorn.org/) - ASGI server for FastAPI.
4. [Streamlit](https://streamlit.io/) - Frontend framework.
5. Other necessary Python libraries as mentioned in `requirements.txt`.

## Step 1: Set Up a Virtual Environment

First, create and activate a virtual environment to isolate your project's dependencies:

```bash
# Create a virtual environment
python -m venv env

# Activate the virtual environment (Windows)
.env\Scripts\activate

# Activate the virtual environment (Linux/macOS)
source env/bin/activate
```

## Step 2: Install Dependencies

Create a `.env` file to store your API keys securely. Add the following line to your `.env` file:
```
API_KEY=your_api_key_here
```

Replace `your_api_key_here` with your actual API key from your AI/ML provider.

Install the required dependencies using `pip`. Create a `requirements.txt` file if not already present with the following content:

```
openai==1.51.0
python-dotenv==1.0.1
fastapi==0.115.0
uvicorn==0.31.0
streamlit==1.39.0
```

Then, install the dependencies:

```bash
pip install -r requirements.txt
```

## Step 3: Running the FastAPI Backend

Ensure that your backend is set up correctly. The backend should handle the `/analyze` endpoint, which the frontend will call to generate AI recommendations.

To start the FastAPI backend, run the following command

```bash
uvicorn backend:idea_analysis --host 0.0.0.0 --port 8000 --reload

This has worked for me:
uvicorn backend.idea_analysis:app --host 0.0.0.0 --port 8000 --reload 
```

## Step 4: Running the Streamlit Frontend

With the backend running, you can now launch the Streamlit frontend. 

```bash
streamlit run frontend/streamlit_test.py
```

This will start a local server, and Streamlit should automatically open the application in your default web browser. If it does not, navigate to [http://localhost:8501](http://localhost:8501).


## Summary

By following these steps, you should have a working **MVP Generator** tool that allows you to generate AI-driven ideas, assess feasibility, and compile reports for potential AI projects. Make sure both your FastAPI and Streamlit servers are running concurrently for full functionality.

If you encounter any problems, check your logs in the terminal for both FastAPI and Streamlit for error messages that can help debug issues.

Enjoy exploring AI solutions for your business! 🚀
