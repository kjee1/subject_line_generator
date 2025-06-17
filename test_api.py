import requests
import json

BASE_URL = "http://127.0.0.1:8000"

# Test newsletter content
test_newsletter = {
    "newsletter_text": "In this week's edition, we explore the latest developments in AI and productivity tools. We'll dive into how GPT-4 is revolutionizing content creation, discuss the impact of AI on remote work, and share tips for maintaining work-life balance in the digital age. Plus, we'll look at emerging trends in workplace automation and how they're shaping the future of work.",
    "audience_profile": "Tech-savvy professionals and startup founders interested in AI and productivity",
    "goal": "Increase open rates by highlighting unique insights and actionable tips",
    "tone": "Professional yet conversational, with a focus on practical insights",
    "past_headlines": [
        "The Future of Work: AI Edition",
        "5 Ways AI is Changing Remote Work",
        "Productivity Hacks for the Digital Age"
    ],
    "constraints": {
        "max_length": 60,
        "avoid_clickbait": True,
        "require_numbers": False
    }
}

def test_provider(provider, model):
    print(f"\nTesting {provider} with model {model}...")
    print("-" * 50)
    
    # Update the request with provider and model
    request_data = test_newsletter.copy()
    request_data["provider"] = provider
    request_data["model"] = model
    
    try:
        response = requests.post(
            f"{BASE_URL}/generate",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("\nGenerated Headlines:")
            for headline in result["headlines"]:
                print(f"\nTitle: {headline['title']}")
                print(f"Keywords: {', '.join(headline['keywords'])}")
                print(f"Reason: {headline['reason']}")
            
            print("\nTrending Topics:")
            for topic in result["trending_topics"]:
                print(f"- {topic}")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Error testing {provider}: {str(e)}")

def main():
    # Test OpenAI
    test_provider("openai", "gpt-4")
    
    # Test Anthropic
    test_provider("anthropic", "claude-3-opus-20240229")
    
    # Test Google (if implemented)
    # test_provider("google", "gemini-pro")

if __name__ == "__main__":
    main() 