# app/models/schemas.py

from pydantic import BaseModel, Field
from typing import List, Optional


class ThemeRequest(BaseModel):
    theme: str
    constraints: List[str] = []


class IdeaConcept(BaseModel):
    name: str
    description: str
    target_audience: Optional[str] = None

class WorkflowStep(BaseModel):
    phase: str
    tasks: List[str]

# NOTE: The WorkflowPlan model from the initial generation is no longer used by the main IdeaResponse
# but is still needed if you want to reuse it internally. We define a new model for the detailed plan.

# 1. Response for the initial /generate endpoint (excludes workflow_plan)
class InitialIdeaResponse(BaseModel):
    problems: List[str]
    existing_solutions: List[str]
    idea_concepts: List[IdeaConcept]
    # workflow_plan is removed here
    
# 2. Request for the new /plan/detailed endpoint
class DetailedPlanRequest(BaseModel):
    idea_concept: IdeaConcept
    team_members: int = Field(default=4, description="Number of team members for task allocation.")
    duration_hours: int = Field(default=48, description="Total duration of the hackathon in hours (e.g., 48h).")
    jira_access_token: Optional[str] = None  # Populated from frontend (e.g., storedAccessToken from query param or storage)
    jira_cloud_id: Optional[str] = None
    # NEW FIELD for Jira/Website Context
    existing_context_url: Optional[str] = Field(
        None, 
        description="URL of an existing website or Jira project/issue to use as planning context (e.g., a Jira Project Key, URL, or JQL)."
    )
# 3. Response for the new /plan/detailed endpoint
class DetailedPlanResponse(BaseModel):
    idea_name: str
    work_process: str = Field(description="Suggested work process (e.g., Scrum, Kanban) and its adaptation for a hackathon.")
    timeline_summary: str = Field(description="A summary of the timeline and phase distribution over the given duration.")
    suggested_tech_stack: List[str] = Field(description="Key technologies, frameworks, and tools suggested, potentially with relevant links.")
    plan_steps: List[WorkflowStep]
