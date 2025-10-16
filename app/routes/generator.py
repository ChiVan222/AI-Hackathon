from fastapi import APIRouter
from app.models.schemas import ThemeRequest,InitialIdeaResponse,DetailedPlanRequest,DetailedPlanResponse
from app.services.idea_generator import generate_ideas
from app.services.plan import generate_detailed_plan
router = APIRouter(prefix="/api", tags=["Hackathon AI"])

@router.post("/generate", response_model=InitialIdeaResponse)
async def generate_endpoint(request: ThemeRequest):
    return await generate_ideas(request)
@router.post("/plan/detailed", response_model=DetailedPlanResponse)
async def plan_detailed_endpoint(request: DetailedPlanRequest):
    """Generates a detailed project plan for a specific idea concept, including timeline and tech stack."""
    return await generate_detailed_plan(request)