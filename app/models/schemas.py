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

class InitialIdeaResponse(BaseModel):
    problems: List[str]
    existing_solutions: List[str]
    idea_concepts: List[IdeaConcept]

class DetailedPlanRequest(BaseModel):
    idea_concept: IdeaConcept
    team_members: int = Field(default=4, description="Number of team members for task allocation.")
    duration_hours: int = Field(default=48, description="Total duration of the hackathon in hours (e.g., 48h).")
    jira_access_token: Optional[str] = None  
    jira_cloud_id: Optional[str] = None
    existing_context_url: Optional[str] = Field(
        None, 
        description="URL of an existing website or Jira project/issue to use as planning context (e.g., a Jira Project Key, URL, or JQL)."
    )
class DetailedPlanResponse(BaseModel):
    idea_name: str
    work_process: str = Field(description="Suggested work process (e.g., Scrum, Kanban) and its adaptation for a hackathon.")
    timeline_summary: str = Field(description="A summary of the timeline and phase distribution over the given duration.")
    suggested_tech_stack: List[str] = Field(description="Key technologies, frameworks, and tools suggested, potentially with relevant links.")
    plan_steps: List[WorkflowStep]
