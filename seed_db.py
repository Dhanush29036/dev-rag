import csv
import chromadb
from chromadb.config import Settings
import uuid
import os

def load_data():
    csv_file = "full_flattened_QA.csv"
    documents = []
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)
        
        for row in reader:
            for cell in row:
                cell = cell.strip()
                if cell:  # If the cell is not empty
                    documents.append(cell)
                    
    print(f"Found {len(documents)} documents to insert.")
    
    if documents:
        print("Initializing ChromaDB...")
        client = chromadb.PersistentClient(path="./chroma_db")
        collection = client.get_or_create_collection(name="rag_docs")
        
        ids = [str(uuid.uuid4()) for _ in documents]
        
        # Batch insert to avoid potential limits
        batch_size = 50
        for i in range(0, len(documents), batch_size):
            batch_docs = documents[i:i+batch_size]
            batch_ids = ids[i:i+batch_size]
            collection.add(
                documents=batch_docs,
                ids=batch_ids
            )
            print(f"Inserted batch {i//batch_size + 1}")
            
        print("Successfully loaded data into ChromaDB 'rag_docs' collection.")

if __name__ == "__main__":
    load_data()
