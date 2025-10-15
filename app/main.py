from fastapi import FastAPI
from app.routes import generator

app = FastAPI(
    title="Hackathon Idea Generator API",
    description="Applies computational thinking to generate hackathon ideas.",
    version="1.0.0"
)

app.include_router(generator.router)

@app.get("/")
def read_root():
    return {"message": "Hackathon AI API is running"}
