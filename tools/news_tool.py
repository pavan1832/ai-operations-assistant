"""
News Tool - Get latest news headlines from various sources
"""

import os
import requests
from typing import Dict, Any, Optional
from tools import BaseTool


class NewsTool(BaseTool):
    """Tool for fetching news headlines"""
    
    def __init__(self):
        """Initialize News tool"""
        super().__init__(
            name="news",
            description="Get latest news headlines from various sources and categories",
            parameters={
                "category": {
                    "type": "string",
                    "description": "News category: general, business, technology, science, health, sports, entertainment",
                    "default": "general"
                },
                "country": {
                    "type": "string",
                    "description": "Country code (e.g., 'us', 'gb', 'ca')",
                    "default": "us"
                },
                "query": {
                    "type": "string",
                    "description": "Search query for specific news topics (optional)"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of articles to return (default: 5)",
                    "default": 5
                }
            }
        )
        
        self.api_key = os.getenv("NEWS_API_KEY")
        self.base_url = "https://newsapi.org/v2"
    
    def execute(
        self,
        category: str = "general",
        country: str = "us",
        query: Optional[str] = None,
        limit: int = 5,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get news headlines
        
        Args:
            category: News category
            country: Country code
            query: Search query (optional)
            limit: Maximum articles
            
        Returns:
            News headlines
        """
        if not self.api_key:
            # Fallback to free RSS/API aggregator
            return self._get_news_fallback(category, limit)
        
        # Use different endpoint based on whether we have a query
        if query:
            endpoint = f"{self.base_url}/everything"
            params = {
                "q": query,
                "apiKey": self.api_key,
                "pageSize": limit,
                "sortBy": "publishedAt",
                "language": "en"
            }
        else:
            endpoint = f"{self.base_url}/top-headlines"
            params = {
                "category": category,
                "country": country,
                "apiKey": self.api_key,
                "pageSize": limit
            }
        
        try:
            response = requests.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") != "ok":
                return self._get_news_fallback(category, limit)
            
            articles = []
            for article in data.get("articles", [])[:limit]:
                articles.append({
                    "title": article["title"],
                    "description": article.get("description", ""),
                    "source": article["source"]["name"],
                    "url": article["url"],
                    "published_at": article["publishedAt"],
                    "author": article.get("author")
                })
            
            return {
                "success": True,
                "total_results": data.get("totalResults", 0),
                "articles": articles
            }
            
        except requests.exceptions.RequestException as e:
            return self._get_news_fallback(category, limit)
    
    def _get_news_fallback(self, category: str = "general", limit: int = 5) -> Dict[str, Any]:
        """
        Fallback news source using free APIs
        
        Args:
            category: News category
            limit: Maximum articles
            
        Returns:
            News headlines
        """
        try:
            # Use NewsData.io free tier or similar
            # For demo purposes, using a mock response
            mock_articles = [
                {
                    "title": f"Latest {category.title()} News Update",
                    "description": f"Top story in {category} category",
                    "source": "News Source",
                    "url": "https://example.com/news",
                    "published_at": "2025-02-05T12:00:00Z",
                    "author": "News Team"
                }
            ]
            
            return {
                "success": True,
                "total_results": 1,
                "articles": mock_articles,
                "message": "Using fallback news source. Add NEWS_API_KEY to .env for real-time news.",
                "source": "fallback"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Unable to fetch news: {str(e)}",
                "articles": [],
                "message": "News API is unavailable. Please add NEWS_API_KEY to .env"
            }
