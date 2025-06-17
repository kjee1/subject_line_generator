from typing import List, Dict
from pydantic import BaseModel

class PromptContext(BaseModel):
    newsletter_text: str
    audience_profile: str
    goal: str
    tone: str
    past_headlines: List[str]
    constraints: Dict
    trending_topics: List[str]

def build_prompt(context: PromptContext) -> str:
    """
    Builds a comprehensive prompt for the LLM based on the provided context.
    """
    prompt = """You are an expert email copywriter trained on millions of high-performing newsletter subject lines.

Your task is to generate 5 unique, high-performing subject lines based on the newsletter content below. Each should:
- Increase open rates
- Be optimized for emotional hooks, curiosity, or relevance
- Avoid overused clichés
- Match the tone and audience provided
- Be under {max_length} characters unless otherwise stated

Also return:
- A list of relevant keywords each subject line targets
- A short explanation of why each subject line is compelling

## Context:
Audience: {audience_profile}
Goal: {goal}
Tone: {tone}
Past high-performing headlines:
{formatted_headlines}

Constraints:
- Maximum length: {max_length} characters
- Avoid clickbait: {avoid_clickbait}
- Require numbers: {require_numbers}

Trending Topics:
{formatted_trends}

## Newsletter Content:
{newsletter_text}

Format your response as a JSON list with the following keys:
- "title"
- "keywords"
- "reason"
""".format(
        max_length=context.constraints.get("max_length", 60),
        audience_profile=context.audience_profile,
        goal=context.goal,
        tone=context.tone,
        formatted_headlines="\n".join(f"- {headline}" for headline in context.past_headlines),
        avoid_clickbait=context.constraints.get("avoid_clickbait", True),
        require_numbers=context.constraints.get("require_numbers", False),
        formatted_trends="\n".join(f"- {topic}" for topic in context.trending_topics),
        newsletter_text=context.newsletter_text
    )
    
    return prompt 