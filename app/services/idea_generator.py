# app/services/idea_generator.py

from app.models.schemas import ThemeRequest, InitialIdeaResponse, IdeaConcept, WorkflowStep
from app.utils.llm_connector import call_llm
import chromadb
from sentence_transformers import SentenceTransformer
import json
import os
import shutil

chroma_client = None
collection = None
embedder = None

def initialize_chroma():
    """Initialize ChromaDB with error handling and recovery."""
    global chroma_client, collection, embedder
    
    if collection is not None:
        return collection
    
    try:
        chroma_client = chromadb.PersistentClient(path="./chroma_db")
        
        try:
            collection = chroma_client.get_collection("hackathon_ideas")
            print(" ChromaDB collection loaded successfully")
        except (KeyError, Exception) as e:
            print(f" Error loading collection: {e}")
            print(" Recreating ChromaDB collection...")
            
            try:
                chroma_client.delete_collection("hackathon_ideas")
            except:
                pass
            
            collection = chroma_client.create_collection(
                name="hackathon_ideas",
                metadata={"description": "Hackathon ideas for RAG retrieval"}
            )
            print("New ChromaDB collection created")
            
        embedder = SentenceTransformer("all-MiniLM-L6-v2")
        return collection
        
    except Exception as e:
        print(f"Fatal ChromaDB error: {e}")
        print("Continuing without RAG retrieval...")
        return None

def normalize_llm_output(data: dict):
    """Normalize LLM output to match the InitialIdeaResponse/IdeaConcept schema structure."""

    concepts = data.get("idea_concepts", [])
    normalized_concepts = []
    for c in concepts:
        if isinstance(c, str):
            normalized_concepts.append(IdeaConcept(name=c, description=""))
        elif isinstance(c, dict):
            if 'title' in c and 'name' not in c:
                c['name'] = c.pop('title')
            normalized_concepts.append(IdeaConcept(**c))
    data["idea_concepts"] = normalized_concepts


    if "workflow_plan" not in data:
         data["workflow_plan"] = [] 

    return data

async def generate_ideas(request: ThemeRequest) -> InitialIdeaResponse:
    
    collection = initialize_chroma()
    

    retrieved_context = "No past ideas available."
    
    if collection is not None and embedder is not None:
        try:
            theme_embedding = embedder.encode(request.theme).tolist()
            
            results = collection.query(
                query_embeddings=[theme_embedding],
                n_results=3, # Retrieve top 3 results
                include=['documents']
            )
            
            if results and results.get('documents') and results['documents'][0]:
                retrieved_context = "\n".join(
                    f"- {doc}" for doc in results['documents'][0]
                )
                print(f" Retrieved {len(results['documents'][0])} similar ideas")
            else:
                retrieved_context = "No closely related ideas found in the database."
                
        except Exception as e:
            print(f" RAG Retrieval Error: {e}")
            retrieved_context = "Could not retrieve past ideas due to an error. Rely on general knowledge."
    else:
        print("ChromaDB not available, proceeding without RAG retrieval")

    prompt = f"""
You are a Hackathon Idea Analysis Assistant.
We are analyzing the theme: "{request.theme}".
Constraints: {request.constraints}.

Based on related past hackathon ideas below, infer the real-world problems they are solving.

Related hackathon ideas:
{retrieved_context}

Tasks:
1. Identify the **underlying real-world problems** inferred from these ideas.
2. Summarize **existing solution approaches** (based on common trends).
3. Propose **new innovative ideas** that combine or extend them. **(Use 'name' and 'description' fields for ideas)**
4. Outline a **simple, high-level workflow plan** for implementation.

Ensure that `idea_concepts` and `workflow_plan` are arrays of JSON objects, not plain strings.

Return the answer strictly as a valid JSON object:
{{
    "problems": [ ... ],
    "existing_solutions": [ ... ],
    "idea_concepts": [ {{"name": "...", "description": "..."}} ],
    "workflow_plan": [ {{"step": "...", "description": "..."}} ]
}}
"""

    raw_response = await call_llm(prompt)
    print(" Raw LLM Response:", raw_response)

    if isinstance(raw_response, dict):
         data = raw_response
    else:
      cleaned = raw_response.strip()
      if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        cleaned = cleaned.replace("json", "", 1).strip()

      try:
        data = json.loads(cleaned)
      except Exception as e:
        print(" JSON parse error:", e)
        print("Raw output:\n", cleaned)
        raise
      
    data = normalize_llm_output(data)

    return InitialIdeaResponse(**data)