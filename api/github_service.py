import requests
import logging
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class GitHubService:
    def __init__(self, token: Optional[str] = None):
        self.token = token
        self.headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        if token:
            self.headers["Authorization"] = f"token {token}"

    def _get_repo_owner_name(self, repo_url: str) -> tuple[str, str]:
        parsed_url = urlparse(repo_url)
        path_parts = parsed_url.path.strip('/').split('/')
        if len(path_parts) < 2:
            raise ValueError("Invalid GitHub URL format")
        owner = path_parts[-2]
        repo = path_parts[-1].replace(".git", "")
        return owner, repo

    def get_issues(self, repo_url: str, state: str = "open", per_page: int = 10) -> List[Dict[str, Any]]:
        owner, repo = self._get_repo_owner_name(repo_url)
        url = f"https://api.github.com/repos/{owner}/{repo}/issues?state={state}&per_page={per_page}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_pull_requests(self, repo_url: str, state: str = "open", per_page: int = 10) -> List[Dict[str, Any]]:
        owner, repo = self._get_repo_owner_name(repo_url)
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls?state={state}&per_page={per_page}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_commits(self, repo_url: str, per_page: int = 10) -> List[Dict[str, Any]]:
        owner, repo = self._get_repo_owner_name(repo_url)
        url = f"https://api.github.com/repos/{owner}/{repo}/commits?per_page={per_page}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
