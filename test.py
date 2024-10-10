from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional
from openai import OpenAI
import json
import logging
import os
from typing import List, Dict, Optional

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class CompetitorContext(BaseModel):
    industry: Optional[str]
    product: Optional[str]
    minimum_viable_product: Optional[str]
    proposed_solution: Optional[str]

class ProductBriefRequest(BaseModel):
    context: CompetitorContext

@app.post("/analyze_competition")
async def analyze_competition(request: ProductBriefRequest):
    """
    Endpoint to generate competitive analysis for a product idea including 
    competitors, features, strengths, and weaknesses.
    """
    try:
        user_prompt = f"""
        Based on the following product brief, provide a detailed competitive analysis.

        Industry: {request.context.industry or 'N/A'}
        Product: {request.context.product or 'N/A'}
        MVP Features: {request.context.minimum_viable_product or 'N/A'}
        Proposed Solution: {request.context.proposed_solution or 'N/A'}

        Your analysis should include:

        For each major competitor (analyze 3-4 competitors):
        - Company name
        - Main features and offerings
        - Key strengths
        - Areas for improvement or weaknesses
        - Market positioning

        Present the information in markdown format with clear sections.
        Additionally, provide a comparison diagram in Mermaid syntax.

        Return only a JSON object with the following structure:
        {{
            "competitive_analysis": {{
                "competitors": [
                    {{
                        "name": "Competitor Name",
                        "description": "Brief description",
                        "features": ["feature1", "feature2"],
                        "strengths": ["strength1", "strength2"],
                        "weaknesses": ["weakness1", "weakness2"],
                        "market_position": "Description of market position"
                    }}
                ]
            }},
            "mermaid_diagram": "graph LR\\n    A[Your Product] --> B[Market]\\n    B --> C[Competitor1]\\n    B --> D[Competitor2]"
        }}
        """

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a market research expert conducting competitive analysis."},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=2000,
            temperature=0.7
        )

        if response and response.choices:
            message = response.choices[0].message.content
            try:
                # Parse the JSON response
                result = json.loads(message)
                
                # Format the response for better readability
                formatted_analysis = {
                    "competitive_analysis": {
                        "market_overview": f"Competitive analysis for {request.context.product}",
                        "competitors": result["competitive_analysis"]["competitors"]
                    },
                    "mermaid_diagram": result["mermaid_diagram"]
                }
                
                return formatted_analysis
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing error: {e}\nResponse content: {message}")
                raise HTTPException(
                    status_code=500,
                    detail="Failed to parse competitive analysis results"
                )
        else:
            raise HTTPException(
                status_code=500,
                detail="No response received from analysis service"
            )
            
    except Exception as e:
        logger.error(f"Error in competitive analysis: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )