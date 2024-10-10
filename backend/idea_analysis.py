# backend script

import os
import logging
from dotenv import load_dotenv
from openai import OpenAI
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import requests
from typing import Dict
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
    mvp: str

class ProductBriefRequest(BaseModel):
    context: Dict
    website_overview: str

@app.post("/generate_product_brief")
async def generate_product_brief(request: ProductBriefRequest):
    try:
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
            max_tokens=6000,
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
    try:
        user_prompt = f"""
        Analyze this business project and provide a concise JSON response:
        - Domain: {request.domain}
        - Problem: {request.problem}
        - Website: {request.website}
        - MVP: {request.mvp}

        Return only a JSON object with these keys:
        {{
            "industry": "industry category",
            "product": "product type",
            "website": "website URL",
            "minimum_viable_product": "MVP description",
            "business_impact": "expected impact"
        }}
        """

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=4000,
            temperature=0.7
        )

        if response and response.choices:
            message = response.choices[0].message.content
            try:
                structured_response = json.loads(message)
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

@app.post("/generate_tech_stack")
async def generate_tech_stack(request: ProductBriefRequest):
    """
    Endpoint to generate a detailed technical implementation explanation including the tech stack and a system diagram in Mermaid syntax.
    """
    try:
        user_prompt = f"""
        Based on the following product brief, provide a detailed technical implementation plan.

        Industry: {request.context.get('industry', 'N/A')}
        Product: {request.context.get('product', 'N/A')}
        MVP: {request.context.get('minimum_viable_product', 'N/A')}
        Proposed Solution: {request.context.get('proposed_solution', 'N/A')}

        Your explanation should include:

        - **Frontend Technologies**: List and explain the frontend technologies to be used.
        - **Backend Technologies**: List and explain the backend technologies to be used.
        - **Cloud Infrastructure**: Describe the cloud services and infrastructure components.
        - **AI/ML Components**: Detail the AI/ML frameworks and tools to be used.
        - **Database**: Specify the type of database and justification.
        - **APIs and Integration**: Explain how different components will communicate.
        - **Security Measures**: Outline security practices and tools.

        Present the information in markdown format with headings and bullet points under each category.

        Additionally, provide a system diagram in Mermaid syntax that illustrates the architecture. **Ensure the diagram uses 'graph LR' to set the layout direction from left to right (horizontal).**

        Return **only** a JSON object with the following structure, and ensure it is valid JSON:

        ```json
        {{
            "technical_details": "Your detailed explanation here in markdown format.",
            "mermaid_diagram": "Your Mermaid syntax diagram here."
        }}
        ```

        Do not include any additional text or explanations outside the JSON object.
        """

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=2500,
            temperature=0.7
        )

        if response and response.choices:
            message = response.choices[0].message.content
            # Attempt to extract JSON from the response
            try:
                # Use regular expressions to extract the JSON part between ```json and ```
                import re
                json_match = re.search(r"```json\s*(\{.*?\})\s*```", message, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                    result = json.loads(json_str)
                    return result
                else:
                    # If no JSON code block is found, try to parse the entire message
                    result = json.loads(message)
                    return result
            except json.JSONDecodeError as e:
                logging.error(f"JSON parsing error in technical details: {e}\nResponse content: {message}")
                return {
                    "error": "Invalid JSON response from the API.",
                    "raw_response": message
                }
        else:
            return {"error": "No response received from the API."}
    except Exception as e:
        logging.error(f"Error occurred while generating technical details: {e}")
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/generate_market_analysis")
async def generate_market_competitor_analysis(request: ProductBriefRequest):
    """
    Endpoint to generate a market analysis.
    """
    try:
        user_prompt = f"""
        Based on the following product brief, provide a detailed market and competitor analysis:

        Industry: {request.context.get('industry', 'N/A')}
        Product: {request.context.get('product', 'N/A')}
        MVP: {request.context.get('minimum_viable_product', 'N/A')}
        Proposed Solution: {request.context.get('proposed_solution', 'N/A')}

        Your analysis should include:

        - Market Overview: Size, trends, and growth potential.
        - Target Market: Specific segments and demographics.
        - Competitive Landscape: Key competitors, their strengths and weaknesses.
        - Opportunities and Threats: Market gaps and potential challenges.
        - Differentiation: How this product stands out from competitors.

        Provide the response in a structured JSON format with the following keys:

        {{
            "market_overview": "...",
            "target_market": "...",
            "competitive_landscape": "...",
            "opportunities_and_threats": "...",
            "differentiation": "..."
        }}
        """

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=4000,
            temperature=0.7
        )

        if response and response.choices:
            message = response.choices[0].message.content
            try:
                return json.loads(message)
            except json.JSONDecodeError as e:
                logging.error(f"JSON parsing error in market and competitor analysis: {e}\nResponse content: {message}")
                return {
                    "error": "Invalid JSON response from the API.",
                    "raw_response": message
                }
        else:
            return {"error": "No response received from the API."}
    except Exception as e:
        logging.error(f"Error occurred while generating market and competitor analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/complete_analysis")
async def complete_analysis(request: AnalysisRequest):
    try:
        json_response = await prompt_to_json(request)
        if "error" in json_response:
            return json_response
        brief_request = ProductBriefRequest(
            context=json_response["json_analysis"],
            website_overview=json_response["website_overview"]
        )
        product_brief = await generate_product_brief(brief_request)
        return {
            "analysis": json_response,
            "product_brief": product_brief
        }
    except Exception as e:
        logging.error(f"Error occurred in complete analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

### aginerd code starts form here ###
# Define the AnalysisRequest model





# Step 1: Search for competitors based on URL or project idea using GPT-4.0 (with browsing)
async def search_for_competitors(url: str, project_idea: str, domain:str, mvp: str):
    try:
        if url:
            # Focus search on competitors of the given website
            user_prompt = f"""
            - Website: {url}
            Task:
            1. Search for competitor websites related to the project idea and {url}.
            2. Provide a list of the top 5 competitors and their products.
            
            Output:
            1. Competitor Name A
            1.1 Product A
            1.2 Description of Product A
            """
        else:
            # Use project idea alone to find top competitors
            user_prompt = f"""
            - Project Idea: {project_idea}
            Task:
            1. Search the web for top 5 competitors in the field of {project_idea} in {domain} with minimum viable product {mvp}.
            2. Provide a list of the top 5 competitors and their products.
            
            Output:
            1. Competitor Name A
            1.1 Product A
            1.2 Description of Product A
            """
        
        # Use GPT-4.0 with browsing to search for competitors
        response = client.chat.completions.create(
            model="gpt-4",  # The version that has browsing capability
            messages=[
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=700,
            temperature=0.7
        )

        if response and response.choices:
            search_results = response.choices[0].message.content
            print(search_results)
            return search_results  # Raw competitor data for further analysis

        return None
    except Exception as e:
        logging.error(f"Error in browsing: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Step 2: Analyze competitor products for gaps (using GPT-4.01 for reasoning)
async def analyze_competitor_products(competitor_data: str):
    try:
        user_prompt = f"""
        Task:
        1. Analyze the following competitor data.
        2. For each competitor, provide one point where their product is lacking.
        3. Suggest how the user can fill the gap in their own product.

        Competitor Data:
        {competitor_data}

        Output:
        1. Competitor Name A
        1.1 Product A
        1.2 Description of Product A
        1.3 Feature(s) that Product A lacks
        1.4 Suggestion for how the user can implement this missing feature in their product
        """

        # Use GPT-4.01 for deeper analysis
        response = client.chat.completions.create(
            model="gpt-4",  # The reasoning model for deeper analysis
            messages=[
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=1000,
            temperature=0.7
        )

        if response and response.choices:
            analysis_result = response.choices[0].message.content
            return analysis_result

        return None
    except Exception as e:
        logging.error(f"Error in analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
# Main Endpoint to combine both steps (search + analysis)
@app.post("/competition_research")
async def competition_research_analysis(request: AnalysisRequest):
    """
    Step 1: Search for competitors using GPT-4.0
    Step 2: Pass competitor data to GPT-4.01 for deeper analysis
    """
    try:
        # Step 1: Search for competitors based on the URL or project idea
        print("try")
        competitor_data = await search_for_competitors(request.website, request.problem, request.domain, request.mvp) 
        
        if not competitor_data:
            return {"error": "Failed to gather competitor information."}

        # Step 2: Analyze the competitor data to find gaps and suggest improvements
        analysis = await analyze_competitor_products(competitor_data)

        if not analysis:
            return {"error": "Failed to analyze competitor data."}

        return {
            "analysis": analysis
        }

    except Exception as e:
        logging.error(f"Error in complete analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))
### aginerd code ends here ###

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)



#{
#    "url": "https://example.com",
#    "project_idea": "An online learning platform for coding"
#}