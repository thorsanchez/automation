import requests
import pandas as pd
from typing import Optional
import time

# Ætla að nota git open source home assistant (með crashes, bugs, feature requests, UI issues)
REPO_OWNER = "home-assistant"
REPO_NAME = "core"
GITHUB_API_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues"

def fetch_github_issues(
    limit: int = 20,
    # kannski nota all fyrir dashboard seinna?
    state: str = "open",
    since: Optional[str] = None
) -> pd.DataFrame:
    """
    Fetch opin git issues (hugsa .etta sem tickets)
    skmila df með title body number labels og created at
    """
    params = {
        "state": state,
        "sort": "created",
        "direction": "desc",
        "per_page": min(limit, 100),
        "page": 1
    }
    if since:
        params["since"] = since

    headers = {
        "Accept": "application/vnd.github.v3+json",
    }

    try:
        response = requests.get(GITHUB_API_URL, params=params, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Git fetch failed: {e}")

    issues = response.json()

    # hunsa pull requests
    issues = [issue for issue in issues if "pull_request" not in issue]

    if not issues:
        raise ValueError("No issues")

    df = pd.DataFrame(issues)
    
    # endurskyra cols
    df = df[['number', 'title', 'body', 'labels', 'created_at', 'html_url']].copy()
    df.rename(columns={
        "number": "issue_id",
        "body": "description",
        "html_url": "source_url"
    }, inplace=True)

    # extract label names
    df['labels'] = df['labels'].apply(lambda x: [label['name'] for label in x] if x else [])
    
    # Sameina title og description fyrir betra LLM input
    df['text'] = df['title'] + "\n\n" + df['description'].fillna("")

    df = df.head(limit)

    return df[['issue_id', 'text', 'title', 'description', 'labels', 'created_at', 'source_url']]


#test
if __name__ == "__main__":
    df = fetch_github_issues(limit=10, state="open")
    print(df[['title', 'text']].head(3))