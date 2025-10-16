import chromadb
import pandas as pd
from sentence_transformers import SentenceTransformer

# Load CSV
df = pd.read_csv("data/ideas.csv")

# Init persistent vector DB
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection("hackathon_ideas")
embedder = SentenceTransformer("all-MiniLM-L6-v2")

for i, row in df.iterrows():
    text = f"Theme: {row['theme']}\nIdea: {row['idea']}\nDescription: {row['description']}"
    emb = embedder.encode(text).tolist()
    collection.add(documents=[text], embeddings=[emb], ids=[f"idea_{i}"])

print("Knowledge base initialized with", len(df), "ideas.")
