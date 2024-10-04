import os
import logging
from dotenv import load_dotenv
from openai import OpenAI
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

app = FastAPI()

def load_api_key():
    try:
        load_dotenv()
        api_key = os.getenv("API_KEY")
        if not api_key:
            raise ValueError("API key not found. Please add your API_KEY to the .env file.")
        return api_key
    except Exception as e:
        raise RuntimeError(f"Error loading API key: {e}")


base_url = "https://api.aimlapi.com"

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

api_key = load_api_key()
client = OpenAI(api_key=api_key, base_url=base_url)

class AnalysisRequest(BaseModel):
    domain: str
    problem: str

    
@app.post("/analyze")
async def analyze(request: AnalysisRequest):
    try:
        domain = request.domain
        problem = request.problem

        user_prompt = f"""
I am working in the domain of {domain}. The problem I want to solve is: {problem}. I need a comprehensive and detailed analysis that includes the following:

1. **Existing Technical Solutions**: Provide an in-depth overview of current technical solutions available in the market for this problem. Mention notable features of their products from innovative companies.

2. **Market Potential**: Analyze the market potential for this solution, considering trends, growth opportunities, market size, and customer needs. Include data and statistics to support your analysis where possible.

3. **Competitive Landscape**: If this idea is not niche, list the top competitors in this domain, including detailed descriptions of their market position, strategies, customer base, and differentiation.

4. **Gaps and Opportunities**: Identify any gaps in the current solutions where new innovations could provide significant value. Highlight potential opportunities to differentiate a new solution from existing competitors.

5. **Suggestions for Market Fit**: Provide actionable suggestions for how to position this idea in the market, including product features, marketing strategies, and possible partnerships.

Please ensure that all provided information is based on factual data, current industry practices, and well-supported insights. Avoid any speculative or inaccurate information.
"""

        # Make a request to the API
        response = client.chat.completions.create(
            model="o1-preview",
            messages=[
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=8000,
        )
        # Extract the response from the API with error handling
        try:
            if response and response.choices:
                message = response.choices[0].message.content
            else:
                message = "No response received from the API. Please check the input or try again later."
        except (KeyError, AttributeError) as e:
            logging.error(f"Malformed response structure: {e}")
            message = "An error occurred while processing the response from the API. Please try again later."

        print(message)
        return message
    except Exception as e:
        logging.error(f"Error occurred while getting response from API: {e}")
        raise HTTPException(status_code=500, detail=f"Error occurred while getting response from API: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)