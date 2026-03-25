from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from typing import List
import chromadb
from chromadb.config import Settings
import google.generativeai as genai
import uuid

# ----------------------------
# CONFIG
# ----------------------------

# Gemini API Key
genai.configure(api_key="AIzaSyBEpgdT_P7uRLfW42loHwaDDq82CQHwnvY")

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

Context:
{context}

Question:
{request.query}

Answer clearly:
"""

    # Step 4: Gemini LLM call
    response = model.generate_content(prompt)

    return {
        "query": request.query,
        "answer": response.text,
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