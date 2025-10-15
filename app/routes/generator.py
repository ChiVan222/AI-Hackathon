from fastapi import APIRouter
from app.models.schemas import ThemeRequest, IdeaResponse
from app.services.idea_generator import generate_ideas

router = APIRouter(prefix="/api", tags=["Hackathon AI"])

@router.post("/generate", response_model=IdeaResponse)
async def generate_endpoint(request: ThemeRequest):
    return await generate_ideas(request)
