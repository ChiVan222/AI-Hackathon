from app.models.schemas import ThemeRequest, IdeaResponse
from app.utils.llm_connector import call_llm

async def generate_ideas(request: ThemeRequest) -> IdeaResponse:
    prompt = f"""
Apply computational thinking to analyze the theme: "{request.theme}".
Consider constraints: {request.constraints}.
1. Identify main real-world problems.
2. Summarize existing solutions.
3. Suggest 3 innovative hackathon ideas.
4. Outline a simple workflow plan.
Return the answer as structured JSON : 
    problems: List[str]
    existing_solutions: List[str]
    idea_concepts: List[str]
    workflow_plan: List[str]
"""
    response = await call_llm(prompt)
    print("LLM Response:", response) 
    return IdeaResponse(**response)