import chromadb
from app.core.config import settings

def test_query():
    client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIRECTORY)
    collection = client.get_or_create_collection(settings.CHROMA_COLLECTION_NAME)
    print(f"✅ Connected to collection: {collection.name}")

    # Inspect what’s inside
    count = collection.count()
    print(f"Total embeddings: {count}")

    # Run a sample search
    query = "How many vacation days do employees get?"
    results = collection.query(query_texts=[query], n_results=3)

    print("\n🔍 Query:", query)
    for doc, dist in zip(results["metadatas"][0], results["distances"][0]):
        print(f"- {doc['source']} (score: {dist:.4f})")

if __name__ == "__main__":
    test_query()
