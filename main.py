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

    retrieved_docs = results.get("documents", [[]])[0]
    
    # Step 2: Build context
    context = "\n".join(retrieved_docs)

    # Step 3: Create prompt
    prompt = f"""
You are an AI assistant for a specific application/business.

Context:
{context}

Question:
{request.query}

Instructions:
1. Analyze the Context to understand the core topic, application, or business you represent (e.g., Gate Pass, IT solutions, user permissions, vehicles).
2. Determine if the user's Question is strictly related to this specific core topic. 
3. If the Question is about trains, general knowledge, or any outside business/service NOT strongly implied by the Context, reply EXACTLY with "UNRELATED_QUESTION" and nothing else.
4. If the Question IS related to your core topic, check if you can answer it based ONLY on the provided Context.
5. If it is related but the Context does NOT contain enough information to answer it, reply EXACTLY with "UNKNOWN_RELATED_QUESTION" and nothing else.
6. If the Context DOES contain enough information, answer the question clearly using ONLY the context. Always speak in the user's query language.
"""

    # Step 4: Gemini LLM call
    response = model.generate_content(prompt)
    answer_text = response.text.strip()
    
    # Fallback logic based on categories
    if answer_text == "UNRELATED_QUESTION":
        return {
            "query": request.query,
            "answer": "I am an AI assistant for this website and can only answer questions related to our services.",
            "context_used": [],
            "source": "unrelated_rejected"
        }
    elif answer_text == "UNKNOWN_RELATED_QUESTION":
        # The question is related to our domain, but context is insufficient.
        # Fallback: Ask Gemini to answer it using its general knowledge.
        fallback_prompt = f"Please provide a helpful and professional answer to the following question related to our services: {request.query}"
        fallback_response = model.generate_content(fallback_prompt)
        fallback_answer = fallback_response.text.strip()
        
        # Store both the new question and its newly generated answer into the DB
        new_doc = f"Question: {request.query}\nAnswer: {fallback_answer}"
        new_id = str(uuid.uuid4())
        
        try:
            collection.add(
                documents=[new_doc],
                ids=[new_id]
            )
        except Exception as e:
            print(f"Failed to add generative fallback answer to DB: {e}")
            
        return {
            "query": request.query,
            "answer": fallback_answer,
            "context_used": [],
            "source": "generative_fallback_saved"
        }

    return {
        "query": request.query,
        "answer": answer_text,
        "context_used": retrieved_docs,
        "source": "database_context"
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