# app/services/planner.py (NEW FILE)

from app.models.schemas import DetailedPlanRequest, DetailedPlanResponse, IdeaConcept, WorkflowStep
from app.utils.llm_connector import call_llm
import json

async def generate_detailed_plan(request: DetailedPlanRequest) -> DetailedPlanResponse:
    """Generates a detailed project plan with tech stack, timeline, and work process."""
    
    concept = request.idea_concept
    
    prompt = f"""
You are a Hackathon Project Planner.
Your task is to create a detailed implementation plan for the following idea, considering the team constraints.

Idea Name: {concept.name}
Description: {concept.description}

Constraints:
- Team Size: {request.team_members} members.
- Duration: {request.duration_hours} hours (a typical hackathon).
- Focus: Tech stack, timeline, and work process must be included.

Tasks:
1. **Work Process**: Suggest a suitable hackathon work process (e.g., Scrum, Kanban, or a hybrid) based on {request.team_members} members and the {request.duration_hours}-hour duration. Explain its adaptation.
2. **Timeline**: Summarize the distribution of time across phases (e.g., 20% planning, 60% coding, 20% testing).
3. **Tech Stack**: List 3-5 suggested key technologies (libraries, frameworks, services) for the idea and include a relevant link/URL for each.
4. **Detailed Steps**: Create 5-8 logical **phases** and list 3-5 concrete **tasks** for each phase.

Return the answer STRICTLY as a valid JSON object:
{{
    "idea_name": "{concept.name}",
    "work_process": "Suggested work process description...",
    "timeline_summary": "Timeline summary (e.g., Phase 1: 4 hours, Phase 2: 12 hours...)",
    "suggested_tech_stack": [ "Tech Name (URL)", "Tech Name (URL)", "..." ],
    "plan_steps": [
        {{"phase": "Phase Name 1", "tasks": ["Task A", "Task B", "Task C"]}},
        {{"phase": "Phase Name 2", "tasks": ["Task D", "Task E", "Task F"]}}
    ]
}}
"""

    raw_response = await call_llm(prompt)
    print(" Raw LLM Plan Response:", raw_response)
    
    # Assuming call_llm handles basic JSON parsing and returns a dict on success
    if isinstance(raw_response, dict):
        return DetailedPlanResponse(**raw_response)
    else:
        # Re-raise or handle the raw response if LLM connector failed to parse
        raise ValueError("Failed to generate or parse detailed plan from LLM.")