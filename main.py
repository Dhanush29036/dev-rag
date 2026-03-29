from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from typing import List
import chromadb
from chromadb.config import Settings
import google.generativeai as genai
import uuid
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ----------------------------
# CONFIG
# ----------------------------

# Gemini API Key (Set this in your environment variables)
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    # Fallback/Placeholder - replace with actual key if needed for local testing
    # api_key = "YOUR_API_KEY_HERE"
    pass

genai.configure(api_key=api_key)

# Gemini Model
model = genai.GenerativeModel("gemini-2.5-flash")

# ChromaDB setup (persistent)
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="rag_docs")

# FastAPI app
app = FastAPI(title="RAG API (Chroma + Gemini) 🚀")

# ----------------------------
# REQUEST MODELS
# ----------------------------

class AddDocsRequest(BaseModel):
    documents: List[str]

class QueryRequest(BaseModel):
    query: str
    n_results: int = 3


# ----------------------------
# ROOT
# ----------------------------
@app.get("/")
def root():
    return {"message": "RAG API running 🚀"}


# ----------------------------
# ADD DOCUMENTS
# ----------------------------
@app.post("/add-docs")
def add_docs(request: AddDocsRequest):
    ids = [str(uuid.uuid4()) for _ in request.documents]

    collection.add(
        documents=request.documents,
        ids=ids
    )

    return {"status": "Documents added", "count": len(ids)}


# ----------------------------
# RETRIEVE + GENERATE (RAG)
# ----------------------------
@app.post("/chat")
def chat(request: QueryRequest):

    # Step 1: Retrieve relevant docs
    results = collection.query(
        query_texts=[request.query],
        n_results=request.n_results
    )

    retrieved_docs = results["documents"][0]

    # Step 2: Build context
    context = "\n".join(retrieved_docs)

    # Step 3: Create prompt
    prompt = f"""
You are an AI assistant. Answer the question based ONLY on the context below.
Always speak in the users query language.

Context:
{context}

Question:
{request.query}

Answer clearly:
"""

    # Step 4: Gemini LLM call
#    response = model.generate_content(prompt)
    print(results)
    return {
        "query": request.query,
        "answer": "",
        "context_used": retrieved_docs
    }


# ----------------------------
# FILE UPLOAD (Optional)
# ----------------------------
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    content = await file.read()
    text = content.decode("utf-8")

    # simple chunking
    chunks = [text[i:i+500] for i in range(0, len(text), 500)]

    ids = [str(uuid.uuid4()) for _ in chunks]

    collection.add(
        documents=chunks,
        ids=ids
    )

    return {"status": "File processed", "chunks": len(chunks)}