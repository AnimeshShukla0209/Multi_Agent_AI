from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
import os

CHROMA_PATH = "chroma_db"

embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
)

def get_vector_store():
    return Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings
    )

def store_research(topic: str, content: str, source: str = "web"):
    """Chunk and store scraped content into ChromaDB."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = splitter.split_text(content)

    db = get_vector_store()
    db.add_texts(
        texts=chunks,
        metadatas=[{"topic": topic, "source": source} for _ in chunks]
    )
    print(f"Stored {len(chunks)} chunks for topic: {topic}")

def retrieve_relevant_context(topic: str, query: str, k: int = 5) -> str:
    """Retrieve top-k relevant chunks for a query."""
    db = get_vector_store()
    results = db.similarity_search(query, k=k)
    
    if not results:
        return "No relevant context found."

    return "\n\n---\n\n".join([doc.page_content for doc in results])