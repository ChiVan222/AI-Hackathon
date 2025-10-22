# app/services/planner.py

from app.models.schemas import DetailedPlanRequest, DetailedPlanResponse, IdeaConcept, WorkflowStep
from app.utils.llm_connector import call_llm
from app.utils.jira_connector import fetch_jira_project_context, create_jira_issues_from_plan
from typing import List, Dict, Any
import re
import json
import requests

async def generate_detailed_plan(request: DetailedPlanRequest) -> DetailedPlanResponse:
    """
    Generates a detailed project plan and, if Jira credentials are provided,
    syncs tasks to the user’s Jira workspace using OAuth.
    """

    concept = request.idea_concept
    jira_context_text = ""

    # Extract optional Jira OAuth data from the request
    access_token = getattr(request, "jira_access_token", None)
    cloud_id = getattr(request, "jira_cloud_id", None)
    existing_context_url = getattr(request, "existing_context_url", None)

    # -----------------------------------------------
    # STEP 1 — Fetch existing Jira context if available
    # -----------------------------------------------
    if existing_context_url and access_token and cloud_id:
        # Extract the Jira project key from the URL or plain key
        project_key_match = re.search(r"browse/([A-Z]+)", existing_context_url)
        project_key = project_key_match.group(1) if project_key_match else existing_context_url

        try:
            jira_context = await fetch_jira_project_context(project_key, access_token, cloud_id)
            if jira_context:
                context_issues = "\n".join([
                    f"- KEY: {issue['key']}, STATUS: {issue['status']}, SUMMARY: {issue['summary']}"
                    for issue in jira_context
                ])
                jira_context_text = f"""
Existing Project Context (Analyze this carefully and ensure your plan addresses gaps or continues existing work):
---
Project Key: {project_key}
Current Issues:
{context_issues}
---
"""
        except Exception as e:
            print(f"Could not fetch Jira context: {e}")

    # -----------------------------------------------
    # STEP 2 — Generate the project plan with the LLM
    # -----------------------------------------------
    prompt = f"""
You are a Hackathon Project Planner.
Your task is to create a detailed implementation plan for the following idea, considering the team constraints.

Idea Name: {concept.name}
Description: {concept.description}

Constraints:
- Team Size: {request.team_members} members.
- Duration: {request.duration_hours} hours (a typical hackathon).
- Focus: Tech stack, timeline, and work process must be included.

{jira_context_text}

Tasks:
1. **Work Process**: Suggest a suitable hackathon work process (e.g., Scrum, Kanban, or hybrid) for {request.team_members} members and {request.duration_hours} hours.
2. **Timeline**: Summarize time distribution and member roles.
3. **Tech Stack**: Suggest 3–5 key technologies (with URLs).
4. **Detailed Steps**: Create 5–8 phases, each with 3–5 specific tasks.

Return strictly valid JSON:
{{
    "idea_name": "{concept.name}",
    "work_process": "Suggested work process...",
    "timeline_summary": "Timeline summary and role distribution",
    "suggested_tech_stack": ["Tech Name (URL)", "Tech Name (URL)", "..."],
    "plan_steps": [
        {{"phase": "", "tasks": ["Task A", "Task B", "Task C"]}},
        {{"phase": "", "tasks": ["Task D", "Task E", "Task F"]}}
    ]
}}
"""
    raw_response = await call_llm(prompt)
    print("Raw LLM Plan Response:", raw_response)

    if not isinstance(raw_response, dict):
        raise ValueError("Failed to generate or parse detailed plan from LLM.")

    plan_response = DetailedPlanResponse(**raw_response)

    # -----------------------------------------------
    # STEP 3 — Create Jira issues if credentials provided
    # -----------------------------------------------
    if existing_context_url and access_token and cloud_id:
        project_key_match = re.search(r"browse/([A-Z]+)", existing_context_url)
        project_key = project_key_match.group(1) if project_key_match else existing_context_url

        try:
            print(f"🌀 Creating Jira issues for project {project_key} using OAuth...")
            new_keys = await create_jira_issues_from_plan(raw_response, project_key, access_token, cloud_id)
            if new_keys:
                print(f"Successfully created Jira issues: {', '.join(new_keys)}")
            else:
                print("No Jira issues were created.")
        except Exception as e:
            print(f"Jira issue creation failed: {e}")

    return plan_response
