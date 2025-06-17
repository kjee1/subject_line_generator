from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pydantic import BaseModel
from typing import List, Optional, Dict
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Newsletter Headline Generator API",
    description="Generate optimized newsletter subject lines using AI and trending topics",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Input models
class Constraints(BaseModel):
    max_length: int = 60
    avoid_clickbait: bool = True
    require_numbers: bool = False

class HeadlineRequest(BaseModel):
    newsletter_text: str
    audience_profile: str
    goal: str
    tone: str
    past_headlines: List[str]
    constraints: Constraints

class HeadlineResponse(BaseModel):
    title: str
    keywords: List[str]
    reason: str

class GenerateResponse(BaseModel):
    headlines: List[HeadlineResponse]
    trending_topics: List[str]

@app.get("/health")
@limiter.limit("30/minute")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.post("/generate", response_model=GenerateResponse)
@limiter.limit("10/minute")
async def generate_headlines(request: HeadlineRequest):
    """
    Generate optimized newsletter subject lines based on the provided content and context.
    """
    try:
        # TODO: Implement headline generation logic
        # This is a mock response for now
        return {
            "headlines": [
                {
                    "title": "Why You're Only Using 10% of Your Potential",
                    "keywords": ["potential", "growth", "mindset"],
                    "reason": "Uses a curiosity gap and appeals to personal improvement."
                }
            ],
            "trending_topics": ["AI productivity", "Work-life balance"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 