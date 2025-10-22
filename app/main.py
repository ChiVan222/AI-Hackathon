from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import generator
from app.routes import jira_auth

app = FastAPI(
    title="Hackathon Idea Generator API",
    description="Applies computational thinking to generate hackathon ideas.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(generator.router)
app.include_router(jira_auth.router)
@app.get("/")
def read_root():
    return {"message": "Hackathon AI API is running"}
