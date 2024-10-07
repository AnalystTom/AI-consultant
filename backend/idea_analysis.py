import os
import logging
from dotenv import load_dotenv
from openai import OpenAI
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import requests
from typing import Dict, List
import json

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
base_url = "https://api.aimlapi.com"
client = OpenAI(api_key=api_key, base_url=base_url)

class AnalysisRequest(BaseModel):
    domain: str
    problem: str
    website: str
    mvp:str

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
        # Simplified and optimized prompt
        user_prompt = f"""
        Create a concise product brief based on this context:

        Industry: {request.context.get('industry', 'N/A')}
        Product: {request.context.get('product', 'N/A')}
        Website: {request.context.get('website', 'N/A')}
        MVP: {request.context.get('minimum_viable_product', 'N/A')}
        Impact: {request.context.get('business_impact', 'N/A')}

        Additional Context: {request.website_overview}

        Provide a JSON response with these keys:
        {{
            "problem_statement": "Brief description of problem and impact",
            "target_audience": "Core user base",
            "why_it_matters": "Key importance and alignment",
            "proposed_solution": "Core solution and features",
            "success_criteria": "Key success metrics",
            "risks_and_considerations": "Main challenges",
            "next_steps": "Immediate actions",
            "additional_notes": "Key information for teams"
        }}
        
        Keep each section concise and focused on essential information.
        """

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=2000,  # Reduced from 8000 to 2000
            temperature=0.7
        )

        if response and response.choices:
            message = response.choices[0].message.content
            try:
                return json.loads(message)
            except json.JSONDecodeError as e:
                logging.error(f"JSON parsing error in product brief: {e}\nResponse content: {message}")
                return {
                    "error": "Invalid JSON response from the API.",
                    "raw_response": message
                }
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
        # Simplified prompt
        user_prompt = f"""
        Analyze this business project and provide a concise JSON response:
        - Domain: {request.domain}
        - Problem: {request.problem}
        - Website: {request.website}
        - MVP: {request.mvp}

        Return only a JSON object with these keys:
        "industry": industry category
        "product": product type
        "website": website URL
        "minimum_viable_product": MVP description
        "business_impact": expected impact
        """

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=500,
            temperature=0.7
        )

        if response and response.choices:
            message = response.choices[0].message.content
            try:
                structured_response = json.loads(message)
                
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
                
            except json.JSONDecodeError as e:
                logging.error(f"JSON parsing error: {e}\nResponse content: {message}")
                return {
                    "error": "Invalid JSON response from the API.",
                    "raw_response": message
                }
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