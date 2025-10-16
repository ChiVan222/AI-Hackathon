# app/services/idea_generator.py

from app.models.schemas import ThemeRequest, InitialIdeaResponse, IdeaConcept, WorkflowStep
from app.utils.llm_connector import call_llm
import chromadb
from sentence_transformers import SentenceTransformer
import json
import os
import shutil

# Global variables for lazy initialization
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
        
        # Try to get existing collection
        try:
            collection = chroma_client.get_collection("hackathon_ideas")
            print("✅ ChromaDB collection loaded successfully")
        except (KeyError, Exception) as e:
            print(f"⚠️ Error loading collection: {e}")
            print("🔄 Recreating ChromaDB collection...")
            
            # Delete old collection if it exists but is corrupted
            try:
                chroma_client.delete_collection("hackathon_ideas")
            except:
                pass
            
            # Create new collection
            collection = chroma_client.create_collection(
                name="hackathon_ideas",
                metadata={"description": "Hackathon ideas for RAG retrieval"}
            )
            print("✅ New ChromaDB collection created")
            
        embedder = SentenceTransformer("all-MiniLM-L6-v2")
        return collection
        
    except Exception as e:
        print(f"❌ Fatal ChromaDB error: {e}")
        print("⚠️ Continuing without RAG retrieval...")
        return None

def normalize_llm_output(data: dict):
    """Normalize LLM output to match the InitialIdeaResponse/IdeaConcept schema structure."""

    # --- Handle idea_concepts (Fix applied here: title -> name) ---
    concepts = data.get("idea_concepts", [])
    normalized_concepts = []
    for c in concepts:
        if isinstance(c, str):
            normalized_concepts.append(IdeaConcept(name=c, description=""))
        elif isinstance(c, dict):
            # FIX: Rename 'title' key to 'name' to match IdeaConcept schema
            if 'title' in c and 'name' not in c:
                c['name'] = c.pop('title')
            normalized_concepts.append(IdeaConcept(**c))
    data["idea_concepts"] = normalized_concepts

    # --- Handle workflow_plan (Required for LLM output, but will be ignored by InitialIdeaResponse) ---
    # The existing logic is complex, simplify by just ensuring the key is present if the LLM returned it.
    # Note: Pydantic will ignore this field when casting to InitialIdeaResponse.
    if "workflow_plan" not in data:
         data["workflow_plan"] = [] 

    return data

async def generate_ideas(request: ThemeRequest) -> InitialIdeaResponse:
    
    # ----------------------------------------------------
    # Initialize ChromaDB (lazy loading with error handling)
    # ----------------------------------------------------
    collection = initialize_chroma()
    
    # ----------------------------------------------------
    # NEW CODE: Retrieval-Augmented Generation (RAG) Logic
    # ----------------------------------------------------
    
    retrieved_context = "No past ideas available."
    
    if collection is not None and embedder is not None:
        try:
            # Embed the theme from the request
            theme_embedding = embedder.encode(request.theme).tolist()
            
            # Retrieve similar documents (past ideas) from ChromaDB
            results = collection.query(
                query_embeddings=[theme_embedding],
                n_results=3, # Retrieve top 3 results
                include=['documents']
            )
            
            # Format the retrieved context for the prompt
            if results and results.get('documents') and results['documents'][0]:
                retrieved_context = "\n".join(
                    f"- {doc}" for doc in results['documents'][0]
                )
                print(f"✅ Retrieved {len(results['documents'][0])} similar ideas")
            else:
                retrieved_context = "No closely related ideas found in the database."
                
        except Exception as e:
            # Fallback if the database or embedding process fails
            print(f"⚠️ RAG Retrieval Error: {e}")
            retrieved_context = "Could not retrieve past ideas due to an error. Rely on general knowledge."
    else:
        print("⚠️ ChromaDB not available, proceeding without RAG retrieval")

    # ----------------------------------------------------
    # Step 4: Build LLM prompt with retrieved context
    # ----------------------------------------------------
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

    # Step 5: Generate with LLM
    raw_response = await call_llm(prompt)
    print(" Raw LLM Response:", raw_response)

    # ... (JSON parsing and normalization)
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
        print("❌ JSON parse error:", e)
        print("Raw output:\n", cleaned)
        raise
      
    data = normalize_llm_output(data)

    # Pydantic automatically ignores the 'workflow_plan' field when casting to InitialIdeaResponse
    return InitialIdeaResponse(**data)