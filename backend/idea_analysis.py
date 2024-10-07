import os
import logging
from dotenv import load_dotenv
import openai
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import json
from typing import Dict

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

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize OpenAI client
api_key = load_api_key()
openai.api_key = api_key

class AnalysisRequest(BaseModel):
    domain: str
    problem: str
    website: str
    mvp: str

class WebsiteRequest(BaseModel):
    website: str

class ProductBriefRequest(BaseModel):
    context: Dict
    website_overview: str

@app.post("/generate_product_brief")
async def generate_product_brief(request: ProductBriefRequest):
    """
    Endpoint to generate a product brief based on the website overview and JSON context.
    """
    try:
        # Define the function schema
        product_brief_schema = {
            "name": "generate_product_brief",
            "description": "Generates a concise product brief based on provided context.",
            "parameters": {
                "type": "object",
                "properties": {
                    "problem_statement": {"type": "string", "description": "Brief description of problem and impact"},
                    "target_audience": {"type": "string", "description": "Core user base"},
                    "why_it_matters": {"type": "string", "description": "Key importance and alignment"},
                    "proposed_solution": {"type": "string", "description": "Core solution and features"},
                    "success_criteria": {"type": "string", "description": "Key success metrics"},
                    "risks_and_considerations": {"type": "string", "description": "Main challenges"},
                    "next_steps": {"type": "string", "description": "Immediate actions"},
                    "additional_notes": {"type": "string", "description": "Key information for teams"}
                },
                "required": [
                    "problem_statement", "target_audience", "why_it_matters",
                    "proposed_solution", "success_criteria", "risks_and_considerations",
                    "next_steps"
                ]
            }
        }

        # Create the prompt
        user_prompt = f"""
You are to generate a concise product brief based on the provided context.

Context:
- Industry: {request.context.get('industry', 'N/A')}
- Product: {request.context.get('product', 'N/A')}
- Website: {request.context.get('website', 'N/A')}
- MVP: {request.context.get('minimum_viable_product', 'N/A')}
- Impact: {request.context.get('business_impact', 'N/A')}
- Additional Context: {request.website_overview}

Please provide the product brief by filling in the fields specified in the function parameters.

Ensure that:
- The response is strictly in JSON format compatible with the function schema.
- All fields are completed with relevant information.
- You follow OpenAI's policies to avoid disallowed content.
"""

        response = openai.ChatCompletion.create(
            model="gpt-4-0613",
            messages=[
                {"role": "user", "content": user_prompt.strip()},
            ],
            functions=[product_brief_schema],
            function_call={"name": "generate_product_brief"},
            max_tokens=1000,
            temperature=0.7
        )

        if response and response['choices']:
            message = response['choices'][0]['message']
            if 'function_call' in message:
                function_args = json.loads(message['function_call']['arguments'])
                return function_args
            else:
                logging.error("Assistant did not return a function call.")
                return {"error": "Invalid response from the API."}
        else:
            return {"error": "No response received from the API."}
    except Exception as e:
        logging.error(f"Error occurred while generating product brief: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/prompt_to_json")
async def prompt_to_json(request: AnalysisRequest):
    """
    Endpoint to generate a structured JSON response based on the given domain and problem.
    """
    try:
        # Define the function schema
        business_analysis_schema = {
            "name": "business_analysis",
            "description": "Analyzes a business project and provides structured information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "industry": {"type": "string", "description": "Industry category"},
                    "product": {"type": "string", "description": "Product type"},
                    "website": {"type": "string", "description": "Website URL"},
                    "minimum_viable_product": {"type": "string", "description": "MVP description"},
                    "business_impact": {"type": "string", "description": "Expected impact"}
                },
                "required": ["industry", "product", "website", "minimum_viable_product", "business_impact"]
            }
        }

        # Create the prompt
        user_prompt = f"""
You are to analyze a business project based on the provided information.

Information:
- Domain: {request.domain}
- Problem: {request.problem}
- Website: {request.website}
- MVP: {request.mvp}

Please provide the analysis by filling in the fields specified in the function parameters.

Ensure that:
- The response is strictly in JSON format compatible with the function schema.
- All fields are completed with relevant information.
- You follow OpenAI's policies to avoid disallowed content.
"""

        response = openai.ChatCompletion.create(
            model="gpt-4-0613",
            messages=[
                {"role": "user", "content": user_prompt.strip()},
            ],
            functions=[business_analysis_schema],
            function_call={"name": "business_analysis"},
            max_tokens=500,
            temperature=0.7
        )

        if response and response['choices']:
            message = response['choices'][0]['message']
            if 'function_call' in message:
                structured_response = json.loads(message['function_call']['arguments'])

                # Create a concise website overview
                website_overview = (
                    f"A {structured_response.get('industry', 'N/A')} business developing "
                    f"{structured_response.get('product', 'N/A')}. "
                    f"MVP: {structured_response.get('minimum_viable_product', 'N/A')}. "
                    f"Impact: {structured_response.get('business_impact', 'N/A')}."
                )

                return {
                    "json_analysis": structured_response,
                    "website_overview": website_overview.strip()
                }
            else:
                logging.error("Assistant did not return a function call.")
                return {"error": "Invalid response from the API."}
        else:
            return {"error": "No response received from the API."}
    except Exception as e:
        logging.error(f"Error occurred while getting response from API: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/complete_analysis")
async def complete_analysis(request: AnalysisRequest):
    """
    Endpoint that combines both prompt_to_json and generate_product_brief into a single flow.
    """
    try:
        # First, get the JSON analysis
        json_response = await prompt_to_json(request)

        if "error" in json_response:
            return json_response

        # Create the product brief request
        brief_request = ProductBriefRequest(
            context=json_response["json_analysis"],
            website_overview=json_response["website_overview"]
        )

        # Generate the product brief
        product_brief = await generate_product_brief(brief_request)

        # Return combined results
        return {
            "analysis": json_response,
            "product_brief": product_brief
        }

    except Exception as e:
        logging.error(f"Error occurred in complete analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
