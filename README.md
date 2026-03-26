# Dev-RAG (ChromaDB + Gemini) 🚀

A simple RAG (Retrieval-Augmented Generation) system built with FastAPI, ChromaDB, and Google Gemini.

## Project Structure
- `main.py`: The FastAPI application that handles retrieval and generation.
- `seed_db.py`: Script to populate the ChromaDB collection from a CSV file.
- `full_flattened_QA.csv`: The source dataset containing Q&A pairs for the RAG system.
- `test_rag_api.py`: A comprehensive test script that queries the API with 10 sample questions.

## Setup
1. Install dependencies:
   ```bash
   pip install fastapi uvicorn chromadb google-generativeai requests
   ```
2. Set your Gemini API key as an environment variable:
   - **Windows (PowerShell):** `$env:GEMINI_API_KEY="your_api_key_here"`
   - **Linux/macOS:** `export GEMINI_API_KEY="your_api_key_here"`
3. Ingest the data:
   ```bash
   python seed_db.py
   ```
4. Start the server:
   ```bash
   uvicorn main:app --port 8001
   ```
5. Run tests:
   ```bash
   python test_rag_api.py
   ```

## Note on Rate Limits
The `test_rag_api.py` script includes a 10-second delay between requests to accommodate Gemini's free-tier rate limits.
