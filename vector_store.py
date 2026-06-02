from langchain_core.vectorstores import InMemoryVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_huggingface import HuggingFaceEndpointEmbeddings

import os

embeddings = HuggingFaceEndpointEmbeddings(
    model="sentence-transformers/all-MiniLM-L6-v2",
    huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN"),
)

_store = InMemoryVectorStore(embedding=embeddings)

def store_research(topic: str, content: str, source: str = "web"):
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_text(content)
    _store.add_texts(
        texts=chunks,
        metadatas=[{"topic": topic, "source": source} for _ in chunks]
    )
    print(f"Stored {len(chunks)} chunks for topic: {topic}")

def retrieve_relevant_context(topic: str, query: str, k: int = 5) -> str:
    results = _store.similarity_search(query, k=k)
    if not results:
        return "No relevant context found."
    return "\n\n---\n\n".join([doc.page_content for doc in results])