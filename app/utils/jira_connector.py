# app/utils/jira_connector.py (fully corrected for OAuth, API compliance, and deprecations, with timeline support via dates and epics)
import requests
import re
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

async def fetch_jira_project_context(project_key: str, access_token: str, cloud_id: str) -> Optional[List[dict]]:
    """Fetch project context from Jira using OAuth token."""
    # Use the new enhanced search endpoint (/search/jql POST) as /search is removed (410 Gone)
    search_url = f"https://api.atlassian.com/ex/jira/{cloud_id}/rest/api/3/search/jql"
    jql_query = f'project = "{project_key}" ORDER BY created DESC'
    payload = {
        "jql": jql_query,
        "fields": ["summary", "status", "description"],  # Must be an array
        "maxResults": 50
    }

    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    try:
        response = requests.post(search_url, headers=headers, json=payload)
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
    except requests.RequestException as e:
        print(f"Failed to fetch Jira context: {e} - Response: {e.response.text if e.response else 'No response'}")
        return None

async def get_project_id(project_key: str, access_token: str, cloud_id: str) -> str:
    """Fetch the project ID by key using OAuth token."""
    url = f"https://api.atlassian.com/ex/jira/{cloud_id}/rest/api/3/project/{project_key}"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    return data["id"]

async def get_issuetype_id(project_id: str, issuetype_name: str, access_token: str, cloud_id: str) -> str:
    """Fetch the issuetype ID by name in the project using createmeta."""
    url = f"https://api.atlassian.com/ex/jira/{cloud_id}/rest/api/3/issue/createmeta?projectIds={project_id}&expand=projects.issuetypes.fields"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    
    for project in data.get("projects", []):
        for issuetype in project.get("issuetypes", []):
            if issuetype["name"].lower() == issuetype_name.lower():
                return issuetype["id"]
    raise ValueError(f"Issuetype '{issuetype_name}' not found in project {project_id}")

async def get_field_info(project_id: str, field_name: str, access_token: str, cloud_id: str) -> Optional[Dict[str, Any]]:
    """Fetch the field ID and schema type by name in the project using createmeta."""
    url = f"https://api.atlassian.com/ex/jira/{cloud_id}/rest/api/3/issue/createmeta?projectIds={project_id}&expand=projects.issuetypes.fields"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    
    for project in data.get("projects", []):
        for issuetype in project.get("issuetypes", []):
            for field_key, field in issuetype.get("fields", {}).items():
                if field.get("name", "").lower() == field_name.lower():
                    return {"id": field_key, "type": field.get("schema", {}).get("type", "string")}
    return None

def text_to_adf(text: str) -> Dict[str, Any]:
    """Convert plain text to Atlassian Document Format (ADF). Handles newlines as paragraphs."""
    paragraphs = text.split("\n\n")  # Split on double newlines for paragraphs
    content = []
    for para in paragraphs:
        para_content = [{"type": "text", "text": line} for line in para.split("\n") if line.strip()]
        if para_content:
            content.append({
                "type": "paragraph",
                "content": para_content
            })
    return {
        "type": "doc",
        "version": 1,
        "content": content
    }

async def create_jira_issues_from_plan(plan_data: Dict[str, Any], project_key: str, access_token: str, cloud_id: str) -> List[str]:
    """Create issues in Jira project using OAuth token, with timeline support via Epics for phases and dates."""
    create_url = f"https://api.atlassian.com/ex/jira/{cloud_id}/rest/api/3/issue"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

    # Fetch required IDs
    try:
        project_id = await get_project_id(project_key, access_token, cloud_id)
        epic_issuetype_id = await get_issuetype_id(project_id, "Epic", access_token, cloud_id)
        task_issuetype_id = await get_issuetype_id(project_id, "Task", access_token, cloud_id)
        epic_link_field = await get_field_info(project_id, "Epic Link", access_token, cloud_id)
        epic_link_id = epic_link_field["id"] if epic_link_field else None
        start_date_field = await get_field_info(project_id, "Start date", access_token, cloud_id)
        start_date_id = start_date_field["id"] if start_date_field else None
        start_date_is_datetime = start_date_field and start_date_field["type"] == "datetime"
        due_date_is_datetime = False  # duedate is always date-only
    except Exception as e:
        print(f"Failed to fetch project, issuetype, or custom field IDs: {e}")
        return []

    base_description_text = (
        f"Idea: {plan_data['idea_name']}\n\n"
        f"Work Process: {plan_data['work_process']}\n"
        f"Timeline: {plan_data['timeline_summary']}\n"
        f"Tech Stack: {', '.join(plan_data['suggested_tech_stack'])}\n\n"
    )

    # Assume hackathon starts now for date calculations (can be parameterized if needed)
    start_time = datetime.now()  # Includes current time for hour-specific calculations

    new_keys = []
    phase_to_epic_key = {}  # Map phase to its Epic key

    # First, create Epics for each phase (to represent timeline blocks)
    for step in plan_data.get("plan_steps", []):
        phase = step["phase"]
        description_text = base_description_text + f"Phase: {phase}\nTasks: {', '.join(step['tasks'])}"

        # Parse hours from phase name, e.g., "(Hours 0-4)"
        match = re.search(r"\(Hours (\d+)-(\d+)\)", phase)
        start_hour = int(match.group(1)) if match else 0
        end_hour = int(match.group(2)) if match else 0

        phase_start_time = start_time + timedelta(hours=start_hour)
        phase_end_time = start_time + timedelta(hours=end_hour)

        # Append hour-specific info to description
        description_text += f"\n\nEstimated Start: {phase_start_time.strftime('%Y-%m-%d %H:%M')}"
        description_text += f"\nEstimated End: {phase_end_time.strftime('%Y-%m-%d %H:%M')}"

        epic_payload = {
            "fields": {
                "project": {"id": project_id},
                "summary": phase,
                "description": text_to_adf(description_text),
                "issuetype": {"id": epic_issuetype_id},
            }
        }

        # Set due date (date only)
        epic_payload["fields"]["duedate"] = phase_end_time.strftime("%Y-%m-%d")

        # Set start date if field exists
        if start_date_id:
            if start_date_is_datetime:
                epic_payload["fields"][start_date_id] = phase_start_time.strftime("%Y-%m-%dT%H:%M:%S.000+0000")  # ISO datetime
            else:
                epic_payload["fields"][start_date_id] = phase_start_time.strftime("%Y-%m-%d")  # Date only

        try:
            res = requests.post(create_url, headers=headers, json=epic_payload)
            if res.status_code == 201:
                epic_key = res.json()["key"]
                new_keys.append(epic_key)
                phase_to_epic_key[phase] = epic_key
            else:
                print(f"Failed to create Epic for phase {phase}: {res.status_code} - {res.text}")
        except Exception as e:
            print(f"Exception creating Epic for phase {phase}: {e}")

    # Then, create Tasks for each task, linked to the phase Epic via Epic Link (if field found)
    for step in plan_data.get("plan_steps", []):
        phase = step["phase"]
        epic_key = phase_to_epic_key.get(phase)

        # Parse hours again for tasks (inherit from phase)
        match = re.search(r"\(Hours (\d+)-(\d+)\)", phase)
        start_hour = int(match.group(1)) if match else 0
        end_hour = int(match.group(2)) if match else 0

        task_start_time = start_time + timedelta(hours=start_hour)
        task_end_time = start_time + timedelta(hours=end_hour)

        for task in step["tasks"]:
            description_text = base_description_text + f"Phase: {phase}\nTask: {task}"
            description_text += f"\n\nEstimated Start: {task_start_time.strftime('%Y-%m-%d %H:%M')}"
            description_text += f"\nEstimated End: {task_end_time.strftime('%Y-%m-%d %H:%M')}"

            task_payload = {
                "fields": {
                    "project": {"id": project_id},
                    "summary": task,
                    "description": text_to_adf(description_text),
                    "issuetype": {"id": task_issuetype_id},
                }
            }
            if epic_key and epic_link_id:
                task_payload["fields"][epic_link_id] = epic_key  # Link to Epic

            # Set due date (date only)
            task_payload["fields"]["duedate"] = task_end_time.strftime("%Y-%m-%d")

            # Set start date if field exists
            if start_date_id:
                if start_date_is_datetime:
                    task_payload["fields"][start_date_id] = task_start_time.strftime("%Y-%m-%dT%H:%M:%S.000+0000")  # ISO datetime
                else:
                    task_payload["fields"][start_date_id] = task_start_time.strftime("%Y-%m-%d")  # Date only

            try:
                res = requests.post(create_url, headers=headers, json=task_payload)
                if res.status_code == 201:
                    new_keys.append(res.json()["key"])
                else:
                    print(f"Failed to create task '{task}': {res.status_code} - {res.text}")
            except Exception as e:
                print(f"Exception creating task '{task}': {e}")

    return new_keys