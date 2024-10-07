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

@app.post("/analyze")
async def analyze(request: AnalysisRequest):
    """
    Endpoint to analyze the given domain and problem, providing a comprehensive market analysis.
    """
    try:
        user_prompt = f"""
        I am working in the domain of {request.domain}. The problem I want to solve is: {request.problem}. I need a comprehensive and detailed analysis that includes the following:

        1. **Existing Technical Solutions**: Provide an in-depth overview of current technical solutions available in the market for this problem. Mention notable features of their products from innovative companies.

        2. **Market Potential**: Analyze the market potential for this solution, considering trends, growth opportunities, market size, and customer needs. Include data and statistics to support your analysis where possible.

        3. **Competitive Landscape**: If this idea is not niche, list the top competitors in this domain, including detailed descriptions of their market position, strategies, customer base, and differentiation.

        4. **Gaps and Opportunities**: Identify any gaps in the current solutions where new innovations could provide significant value. Highlight potential opportunities to differentiate a new solution from existing competitors.

        5. **Suggestions for Market Fit**: Provide actionable suggestions for how to position this idea in the market, including product features, marketing strategies, and possible partnerships.

        Please ensure that all provided information is based on factual data, current industry practices, and well-supported insights. Avoid any speculative or inaccurate information.
        """

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=8000,
        )

        if response and response.choices:
            message = response.choices[0].message.content
        else:
            message = "No response received from the API. Please check the input or try again later."

        return {"analysis": message}
    except Exception as e:
        logging.error(f"Error occurred while getting response from API: {e}")
        raise HTTPException(status_code=500, detail=f"Error occurred while getting response from API: {e}")

@app.post("/prompt_to_json")
async def prompt_to_json(request: AnalysisRequest):
    """
    Endpoint to generate a structured JSON response based on the given domain and problem.
    """
    try:
        user_prompt = f"""
        I'm trying to create an app related to {request.domain}. The problem it solves is: {request.problem}. The website of the business is is {request.website}.
        The minimum viable product is {request.mvp}

        Provide a structured response in JSON format with the following keys:
        "industry": What is the industry of the desired project?
        "product": What is the product?
        "business_name": What is the business called?
        "website": What is the website of the business?
        "minimum_viable_product": What is the minimum viable product?
        "business_impact": What is the business impact?

        If there isn't enough information to answer these questions, write "not enough information".
        """

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=500,
        )

        if response and response.choices:
            message = response.choices[0].message.content
            try:
                structured_response = eval(message)  # Assuming the response is a JSON-like string
            except:
                structured_response = {"error": "Invalid JSON response from the API."}
        else:
            structured_response = {"error": "No response received from the API. Please check the input or try again later."}

        return structured_response
    except Exception as e:
        logging.error(f"Error occurred while getting response from API: {e}")
        raise HTTPException(status_code=500, detail=f"Error occurred while getting response from API: {e}")

@app.post("/website_overview")
async def website_overview(request: WebsiteRequest):
    """
    Endpoint to provide an overview of the given website and generate research on the competition.
    """
    try:
        website_url = request.website

        # Use a web scraping or website overview API to get information about the website
        try:
            response = requests.get(website_url)
            if response.status_code == 200:
                website_content = response.text[:1000]  # Get a sample of the website content
            else:
                raise ValueError("Failed to fetch the website content.")
        except Exception as e:
            logging.error(f"Error occurred while fetching website content: {e}")
            raise HTTPException(status_code=500, detail=f"Error occurred while fetching website content: {e}")

        # Prompt for generating competition analysis
        user_prompt = f"""
        I have the following website: {website_url}. Provide an overview of this website including its main features, target audience, and purpose. Additionally, provide a competitive analysis including top competitors, their strengths, weaknesses, and market position.
        """

        response = client.chat.completions.create(
            model="4o",
            messages=[
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=8000,
        )

        if response and response.choices:
            message = response.choices[0].message.content
        else:
            message = "No response received from the API. Please check the input or try again later."

        return {
            "website_overview": website_content,
            "competition_analysis": message
        }
    except Exception as e:
        logging.error(f"Error occurred while generating website overview and competition analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Error occurred while generating website overview and competition analysis: {e}")

@app.post("/generate_product_brief")
async def generate_product_brief(request: ProductBriefRequest):
    """
    Endpoint to generate a product brief based on the website overview and JSON context from prompt_to_json.
    """
    try:
        context = request.context
        website_overview = request.website_overview

        user_prompt = f"""
        You are an experienced product manager creating a product brief. Use the following context and additional context to generate the brief.

        Context:
        {json.dumps(context, indent=2)}

        Website Overview:
        {website_overview}

        STEP 1: Question Analysis and Ordering
        First analyze these questions from the product brief template:
        - Who are we solving this problem for?
        - What specific problem are we trying to solve?
        - How does this problem impact our users or business?
        - Why is this problem important to solve now?
        - What evidence demonstrates this is a real and significant problem?
        - How will we know if we've successfully solved this problem?
        - How does solving this problem align with our broader goals or strategy?
        - At a high level, what approach are we considering to solve this problem?
        - What are the key components or features of this solution?
        - What specific metrics or outcomes will indicate success?
        - What are the biggest unknowns or challenges we anticipate?
        - Are there any potential negative impacts we should be aware of?
        - What are the immediate next steps to validate or refine this proposal?
        - Who needs to be involved in the next phase of this project?

        STEP 2: Answer the logically ordered questions using only the provided context:
        - Think step-by-step through each answer
        - Skip questions that cannot be reasonably answered with given context
        - Do not make up or hallucinate information
        - Be clear and concise
        - Show your thinking process for each answer

        STEP 3: Create a final product brief using EXACTLY this template structure:

        1-Pager: [Project Name]

        Problem Statement
        * What specific problem are we trying to solve?
        * How does this problem impact our users or business?

        Target Audience
        * Who are we solving this problem for?
        * (If applicable: what key characteristics define this audience/how are they distinct?)

        Why It Matters
        * Why is this problem important to solve now?
        * What evidence do we have that this is a real and significant problem?
        * How does solving this problem align with our broader goals or strategy?

        Proposed Solution
        * At a high level, what approach are we considering to solve this problem?
        * What are the key components or features of this solution?

        Success Criteria
        * How will we know if we've successfully solved this problem?
        * (If applicable: What metrics or outcomes will indicate success?)

        Risks and Considerations
        * What are the biggest unknowns or challenges we anticipate?
        * Are there any potential negative impacts we should be aware of?

        Next Steps
        * What are the immediate next steps to validate or refine this proposal?
        * Who needs to be involved in the next phase of this project?

        Additional Notes
        * Any other clear decisions made or important information relevant to the engineering, design, and/or marketing teams.
        """

        response = client.chat.completions.create(
            model="4o",
            messages=[
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=8000,
        )

        if response and response.choices:
            message = response.choices[0].message.content
        else:
            message = "No response received from the API. Please check the input or try again later."

        return json.loads(message)
    except Exception as e:
        logging.error(f"Error occurred while generating product brief: {e}")
        raise HTTPException(status_code=500, detail=f"Error occurred while generating product brief: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)