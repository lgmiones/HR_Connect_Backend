# chroma_setup.py
import chromadb
from chromadb.config import Settings

def get_chroma_client():
    return chromadb.PersistentClient(
        path="./chroma_db",
        settings=Settings(anonymized_telemetry=False)
    )

def get_or_create_collection(collection_name="hr_documents"):
    client = get_chroma_client()
    try:
        collection = client.get_collection(collection_name)
        print(f"✅ Using existing collection: {collection_name}")
    except Exception:
        collection = client.create_collection(
            name=collection_name,
            metadata={"description": "HR policies and manuals"}
        )
        print(f"✅ Created new collection: {collection_name}")
    return collection