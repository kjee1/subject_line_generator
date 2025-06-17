from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
import os
from dotenv import load_dotenv
from headline_generator import HeadlineGenerator
from prompt_builder import PromptContext
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Model configuration
MODEL_CONFIG = {
    "openai": {
        "models": ["gpt-4", "gpt-3.5-turbo"],
        "api_key": os.getenv("OPENAI_API_KEY")
    },
    "anthropic": {
        "models": ["claude-3-opus-20240229", "claude-3-sonnet-20240229"],
        "api_key": os.getenv("ANTHROPIC_API_KEY")
    },
    "google": {
        "models": ["gemini-pro"],
        "api_key": os.getenv("GOOGLE_API_KEY")
    }
}

# Input models
class Constraints(BaseModel):
    max_length: int = Field(default=60, ge=10, le=100)
    avoid_clickbait: bool = Field(default=True)
    require_numbers: bool = Field(default=False)

class HeadlineRequest(BaseModel):
    newsletter_text: str = Field(..., min_length=1)
    audience_profile: Optional[str] = Field(default="")
    goal: Optional[str] = Field(default="")
    tone: str = Field(..., min_length=1)
    past_headlines: List[str] = Field(default_factory=list)
    constraints: Constraints = Field(default_factory=Constraints)
    provider: Literal["openai", "anthropic", "google"] = Field(default="openai")
    model: str = Field(default="gpt-4")

class Headline(BaseModel):
    title: str
    keywords: List[str]
    reason: str

class HeadlineResponse(BaseModel):
    headlines: List[Headline]
    trending_topics: List[str]

class GenerateResponse(BaseModel):
    headlines: List[Headline]
    trending_topics: List[str]

# Initialize headline generator
headline_generator = HeadlineGenerator()

@app.get("/")
async def read_root():
    """Serve the main page"""
    return FileResponse('static/index.html')

@app.get("/health")
@limiter.limit("30/minute")
async def health_check(request: Request):
    """Health check endpoint"""
    return {"status": "healthy"}

@app.post("/generate", response_model=GenerateResponse)
@limiter.limit("10/minute")
def generate_headlines(request: Request, body: HeadlineRequest):
    """
    Generate optimized newsletter subject lines based on the provided content and context.
    """
    try:
        # Validate model selection
        if body.provider not in MODEL_CONFIG:
            raise HTTPException(status_code=400, detail=f"Invalid provider. Choose from: {list(MODEL_CONFIG.keys())}")
        
        if body.model not in MODEL_CONFIG[body.provider]["models"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid model for {body.provider}. Choose from: {MODEL_CONFIG[body.provider]['models']}"
            )

        # Check if API key is available
        api_key = MODEL_CONFIG[body.provider]["api_key"]
        if not api_key:
            raise HTTPException(
                status_code=500,
                detail=f"API key not configured for {body.provider}"
            )

        # Convert constraints to dictionary
        constraints_dict = body.constraints.dict()

        # Generate headlines
        result = headline_generator.generate_headlines(
            body.newsletter_text,
            body.audience_profile,
            body.goal,
            body.tone,
            body.past_headlines,
            constraints_dict,
            body.provider,
            body.model
        )
        
        return result
    except Exception as e:
        logger.error(f"Error generating headlines: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=3000, reload=True) 