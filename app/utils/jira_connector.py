# app/utils/jira_connector.py (revised for OAuth)
import requests
from typing import Optional, List, Dict, Any

async def fetch_jira_project_context(project_key: str, access_token: str, cloud_id: str) -> Optional[List[dict]]:
    """Fetch project context from Jira using OAuth token."""
    search_url = f"https://api.atlassian.com/ex/jira/{cloud_id}/rest/api/3/search"
    jql_query = f'project = "{project_key}" ORDER BY created DESC'
    params = {"jql": jql_query, "fields": "summary,status,description", "maxResults": 50}

    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(search_url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()

    return [
        {
            "key": issue["key"],
            "status": issue["fields"]["status"]["name"],
            "summary": issue["fields"]["summary"],
        }
        for issue in data.get("issues", [])
    ]

async def create_jira_issues_from_plan(plan_data: Dict[str, Any], project_key: str, access_token: str, cloud_id: str) -> List[str]:
    """Create issues in Jira project using OAuth token."""
    create_url = f"https://api.atlassian.com/ex/jira/{cloud_id}/rest/api/3/issue"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

    base_description = (
        f"Idea: {plan_data['idea_name']}\n\n"
        f"Work Process: {plan_data['work_process']}\n"
        f"Timeline: {plan_data['timeline_summary']}\n"
        f"Tech Stack: {', '.join(plan_data['suggested_tech_stack'])}\n\n"
    )

    new_keys = []
    for step in plan_data.get("plan_steps", []):
        for task in step["tasks"]:
            issue_payload = {
                "fields": {
                    "project": {"key": project_key},
                    "summary": f"[{step['phase']}] {task}",
                    "description": base_description + f"Phase: {step['phase']}\nTask: {task}",
                    "issuetype": {"name": "Task"},
                }
            }
            res = requests.post(create_url, headers=headers, json=issue_payload)
            if res.status_code == 201:
                new_keys.append(res.json()["key"])

    return new_keys
