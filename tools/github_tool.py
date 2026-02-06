"""
GitHub Tool - Search repositories and get repository information
"""

import os
import requests
from typing import Dict, Any, List, Optional
from tools import BaseTool


class GitHubTool(BaseTool):
    """Tool for interacting with GitHub API"""
    
    def __init__(self):
        """Initialize GitHub tool"""
        super().__init__(
            name="github",
            description="Search GitHub repositories, get repository details including stars, forks, and descriptions",
            parameters={
                "action": {
                    "type": "string",
                    "description": "Action to perform: 'search' or 'get_repo'",
                    "enum": ["search", "get_repo"]
                },
                "query": {
                    "type": "string",
                    "description": "Search query (for search action)"
                },
                "repo": {
                    "type": "string",
                    "description": "Repository name in format 'owner/repo' (for get_repo action)"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results to return (default: 5)",
                    "default": 5
                },
                "sort": {
                    "type": "string",
                    "description": "Sort results by: stars, forks, updated (default: stars)",
                    "default": "stars"
                }
            }
        )
        
        self.token = os.getenv("GITHUB_TOKEN")
        self.headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"
        
        self.base_url = "https://api.github.com"
    
    def execute(self, action: str = "search", **kwargs) -> Dict[str, Any]:
        """
        Execute GitHub tool action
        
        Args:
            action: Action to perform
            **kwargs: Action-specific parameters
            
        Returns:
            Action results
        """
        if action == "search":
            return self._search_repositories(**kwargs)
        elif action == "get_repo":
            return self._get_repository(**kwargs)
        else:
            raise ValueError(f"Unknown action: {action}")
    
    def _search_repositories(
        self,
        query: str,
        limit: int = 5,
        sort: str = "stars",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Search GitHub repositories
        
        Args:
            query: Search query
            limit: Maximum results
            sort: Sort criterion
            
        Returns:
            Search results
        """
        url = f"{self.base_url}/search/repositories"
        params = {
            "q": query,
            "sort": sort,
            "order": "desc",
            "per_page": min(limit, 100)
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            repositories = []
            for repo in data.get("items", [])[:limit]:
                repositories.append({
                    "name": repo["name"],
                    "full_name": repo["full_name"],
                    "description": repo["description"],
                    "stars": repo["stargazers_count"],
                    "forks": repo["forks_count"],
                    "language": repo["language"],
                    "url": repo["html_url"],
                    "updated_at": repo["updated_at"]
                })
            
            return {
                "success": True,
                "query": query,
                "total_count": data.get("total_count", 0),
                "repositories": repositories
            }
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "repositories": []
            }
    
    def _get_repository(self, repo: str, **kwargs) -> Dict[str, Any]:
        """
        Get detailed information about a specific repository
        
        Args:
            repo: Repository in format 'owner/repo'
            
        Returns:
            Repository details
        """
        url = f"{self.base_url}/repos/{repo}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return {
                "success": True,
                "repository": {
                    "name": data["name"],
                    "full_name": data["full_name"],
                    "description": data["description"],
                    "stars": data["stargazers_count"],
                    "forks": data["forks_count"],
                    "watchers": data["watchers_count"],
                    "language": data["language"],
                    "url": data["html_url"],
                    "created_at": data["created_at"],
                    "updated_at": data["updated_at"],
                    "topics": data.get("topics", []),
                    "license": data.get("license", {}).get("name") if data.get("license") else None
                }
            }
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e)
            }
