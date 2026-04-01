import os
os.environ["GEMINI_API_KEY"] = "mock_key"

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Mock out chromadb and google.generativeai entirely
with patch('chromadb.PersistentClient') as mock_chromadb_client, \
     patch('google.generativeai.GenerativeModel') as mock_genai_model:
    
    # We must import main after the environment and patching
    import main
    
    client = TestClient(main.app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "RAG API running 🚀"}

@patch("main.collection")
def test_add_docs(mock_collection):
    req_body = {"documents": ["Test document 1", "Test document 2"]}
    response = client.post("/add-docs", json=req_body)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Documents added"
    assert data["count"] == 2

@patch("main.collection")
@patch("main.model")
def test_chat_unrelated(mock_model, mock_collection):
    # Setup mock collection
    mock_collection.query.return_value = {
        "documents": [["Context doc 1"]]
    }
    # Setup mock generative model response
    mock_response = MagicMock()
    mock_response.text = "UNRELATED_QUESTION"
    mock_model.generate_content.return_value = mock_response

    req_body = {"query": "Tell me about trains", "n_results": 1}
    response = client.post("/chat", json=req_body)
    
    assert response.status_code == 200
    data = response.json()
    assert data["source"] == "unrelated_rejected"

@patch("main.collection")
@patch("main.model")
def test_chat_success(mock_model, mock_collection):
    mock_collection.query.return_value = {
        "documents": [["Valid context"]]
    }
    mock_response = MagicMock()
    mock_response.text = "This is a valid answer from context."
    mock_model.generate_content.return_value = mock_response

    req_body = {"query": "Tell me about Gate Pass", "n_results": 1}
    response = client.post("/chat", json=req_body)
    
    assert response.status_code == 200
    data = response.json()
    assert data["source"] == "database_context"
    assert data["answer"] == "This is a valid answer from context."
