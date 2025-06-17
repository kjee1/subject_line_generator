import os
import json
import logging
from typing import List, Dict
from openai import OpenAI
from prompt_builder import PromptContext, build_prompt
from trends_fetcher import TrendsFetcher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HeadlineGenerator:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.trends_fetcher = TrendsFetcher()
        
    async def generate_headlines(self, context: PromptContext) -> Dict:
        """
        Generate headlines using the LLM and incorporate trending topics.
        
        Args:
            context: PromptContext object containing all necessary information
            
        Returns:
            Dictionary containing generated headlines and trending topics
        """
        try:
            # Extract keywords from newsletter text
            keywords = self.trends_fetcher.extract_keywords_from_text(context.newsletter_text)
            
            # Get trending topics
            trending_topics = self.trends_fetcher.get_trending_topics(keywords)
            
            # Update context with trending topics
            context.trending_topics = trending_topics
            
            # Build the prompt
            prompt = build_prompt(context)
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert email copywriter."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            # Parse the response
            try:
                headlines = json.loads(response.choices[0].message.content)
                return {
                    "headlines": headlines,
                    "trending_topics": trending_topics
                }
            except json.JSONDecodeError:
                logger.error("Failed to parse LLM response as JSON")
                return {
                    "headlines": [],
                    "trending_topics": trending_topics
                }
                
        except Exception as e:
            logger.error(f"Error generating headlines: {str(e)}")
            raise 