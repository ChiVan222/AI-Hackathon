from pydantic import BaseModel
from typing import List

class ThemeRequest(BaseModel):
    theme: str
    constraints: List[str] = []

class IdeaResponse(BaseModel):
    problems: List[str]
    existing_solutions: List[str]
    idea_concepts: List[str]
    workflow_plan: List[str]
