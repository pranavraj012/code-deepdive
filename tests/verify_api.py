import asyncio
import httpx
import sys
import os

# Add root directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from api.github_service import GitHubService

async def test_github_service():
    print("Testing GitHubService...")
    service = GitHubService()
    repo_url = "https://github.com/pranavraj012/code-deepdive"
    
    try:
        issues = service.get_issues(repo_url, per_page=1)
        print(f"Successfully fetched {len(issues)} issues")
        
        pulls = service.get_pull_requests(repo_url, per_page=1)
        print(f"Successfully fetched {len(pulls)} pull requests")
        
        commits = service.get_commits(repo_url, per_page=1)
        print(f"Successfully fetched {len(commits)} commits")
    except Exception as e:
        print(f"GitHubService test failed: {e}")

async def test_api_endpoints():
    print("\nTesting API Endpoints (Local)...")
    async with httpx.AsyncClient() as client:
        # Test health
        try:
            resp = await client.get("http://localhost:8000/health")
            print(f"Health check: {resp.status_code}")
        except Exception as e:
            print(f"Health check failed (is the server running?): {e}")

if __name__ == "__main__":
    asyncio.run(test_github_service())
    asyncio.run(test_api_endpoints())
