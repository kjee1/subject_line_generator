from pytrends.request import TrendReq
from typing import List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrendsFetcher:
    def __init__(self):
        self.pytrends = TrendReq(hl='en-US', tz=360)
        
    def get_trending_topics(self, keywords: List[str], timeframe: str = 'now 7-d') -> List[str]:
        """
        Fetch trending topics related to the given keywords using Google Trends.
        
        Args:
            keywords: List of keywords to search for related trends
            timeframe: Time period for trends (default: last 7 days)
            
        Returns:
            List of trending topics
        """
        try:
            # Build payload
            self.pytrends.build_payload(
                kw_list=keywords,
                cat=0,
                timeframe=timeframe,
                geo='',
                gprop=''
            )
            
            # Get related queries
            related_queries = self.pytrends.related_queries()
            
            trending_topics = []
            
            # Extract top rising queries for each keyword
            for keyword in keywords:
                if keyword in related_queries and related_queries[keyword]['top'] is not None:
                    top_queries = related_queries[keyword]['top']
                    if not top_queries.empty:
                        trending_topics.extend(top_queries['query'].head(3).tolist())
            
            return list(set(trending_topics))  # Remove duplicates
            
        except Exception as e:
            logger.error(f"Error fetching trending topics: {str(e)}")
            return []  # Return empty list on error
            
    def extract_keywords_from_text(self, text: str) -> List[str]:
        """
        Extract potential keywords from the newsletter text.
        This is a simple implementation that can be enhanced with NLP.
        
        Args:
            text: Newsletter text to extract keywords from
            
        Returns:
            List of potential keywords
        """
        # Simple implementation - split by spaces and take words longer than 4 chars
        words = text.lower().split()
        keywords = [word for word in words if len(word) > 4]
        
        # Remove common words (can be expanded)
        common_words = {'about', 'their', 'there', 'would', 'could', 'should', 'which', 'where', 'when'}
        keywords = [word for word in keywords if word not in common_words]
        
        return keywords[:5]  # Return top 5 keywords 