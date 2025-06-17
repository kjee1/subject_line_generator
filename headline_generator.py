import os
import json
import logging
from typing import List, Dict, Any
from openai import OpenAI
from anthropic import Anthropic
import google.generativeai as genai
from prompt_builder import PromptContext, build_prompt
from trends_fetcher import TrendsFetcher

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HeadlineGenerator:
    def __init__(self):
        self.trends_fetcher = TrendsFetcher()
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

    def generate_headlines(
        self,
        newsletter_text: str,
        audience_profile: str,
        goal: str,
        tone: str,
        past_headlines: List[str],
        constraints: Dict[str, Any],
        provider: str = "openai",
        model: str = "gpt-4"
    ) -> Dict[str, Any]:
        """
        Generate headlines using the specified LLM provider and model.
        """
        try:
            # Extract keywords and get trending topics
            keywords = self.trends_fetcher.extract_keywords_from_text(newsletter_text)
            trending_topics = self.trends_fetcher.get_trending_topics(keywords)

            # Build context and prompt
            context = PromptContext(
                newsletter_text=newsletter_text,
                audience_profile=audience_profile,
                goal=goal,
                tone=tone,
                past_headlines=past_headlines,
                constraints=constraints,
                trending_topics=trending_topics
            )
            prompt = build_prompt(context)

            # Generate headlines based on provider
            if provider == "openai":
                headlines = self._generate_with_openai(prompt, model)
            elif provider == "anthropic":
                headlines = self._generate_with_anthropic(prompt, model)
            elif provider == "google":
                headlines = self._generate_with_google(prompt, model)
            else:
                raise ValueError(f"Unsupported provider: {provider}")

            return {
                "headlines": headlines,
                "trending_topics": trending_topics
            }

        except Exception as e:
            logger.error(f"Error in generate_headlines: {str(e)}")
            raise

    def _generate_with_openai(self, prompt: str, model: str) -> List[Dict[str, Any]]:
        """
        Generate headlines using OpenAI's API.
        """
        try:
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are an expert newsletter headline writer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            # Parse the response
            content = response.choices[0].message.content
            try:
                headlines = json.loads(content)
                if not isinstance(headlines, list):
                    raise ValueError("Response is not a list of headlines")
                return headlines
            except json.JSONDecodeError:
                logger.error(f"Failed to parse OpenAI response: {content}")
                raise ValueError("Failed to parse LLM response")

        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise

    def _generate_with_anthropic(self, prompt: str, model: str = "claude-3-opus-20240229") -> List[Dict[str, Any]]:
        """Generate headlines using Anthropic's Claude model."""
        try:
            response = self.anthropic_client.messages.create(
                model=model,
                max_tokens=1000,
                temperature=0.7,
                system="You are a professional headline generator. Generate headlines in JSON format.",
                messages=[{"role": "user", "content": prompt}]
            )
            content = response.content[0].text
            logger.info(f"Raw Claude response: {content}")
            
            # Extract JSON array from response
            start_idx = content.find('[')
            end_idx = content.rfind(']') + 1
            if start_idx == -1 or end_idx == 0:
                raise ValueError("No JSON array found in response")
            
            json_str = content[start_idx:end_idx]
            headlines = json.loads(json_str)
            
            if not isinstance(headlines, list):
                raise ValueError("Response is not a list")
            
            return headlines
        except Exception as e:
            logger.error(f"Anthropic API error: {str(e)}")
            raise 

    def _generate_with_google(self, prompt: str, model: str = "gemini-pro") -> List[Dict[str, Any]]:
        """Generate headlines using Google's Gemini model."""
        try:
            logger.info("Listing available models:")
            for m in genai.list_models():
                logger.info(f"Model: {m.name}")
            
            logger.info(f"Initializing Google Gemini model: {model}")
            model = genai.GenerativeModel(model)
            logger.info("Model initialized successfully")
            
            logger.info("Generating content with prompt")
            response = model.generate_content(
                f"""You are a professional headline generator. Generate headlines in JSON format.
                {prompt}""",
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": 1000,
                }
            )
            logger.info("Content generated successfully")
            
            content = response.text
            logger.info(f"Raw Gemini response: {content}")
            
            # Extract JSON array from response
            start_idx = content.find('[')
            end_idx = content.rfind(']') + 1
            if start_idx == -1 or end_idx == 0:
                logger.error("No JSON array found in response")
                raise ValueError("No JSON array found in response")
            
            json_str = content[start_idx:end_idx]
            logger.info(f"Extracted JSON string: {json_str}")
            
            headlines = json.loads(json_str)
            logger.info(f"Parsed headlines: {headlines}")
            
            if not isinstance(headlines, list):
                logger.error("Response is not a list")
                raise ValueError("Response is not a list")
            
            return headlines
        except Exception as e:
            logger.error(f"Google API error: {str(e)}")
            raise 