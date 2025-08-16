# precompute_vector_store.py
import os
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_chroma import Chroma

DOCS_DIR = os.getenv("DOCS_DIR", "ghc_docs")
VECTOR_STORE_DIR = os.getenv("VECTOR_STORE_DIR", "vector_store")
EMBED_MODEL = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-large")

def ingest_documents():
    embeddings = OpenAIEmbeddings(model=EMBED_MODEL)
    db = Chroma(persist_directory=VECTOR_STORE_DIR, embedding_function=embeddings)
    docs = []
    for filename in os.listdir(DOCS_DIR):
        if filename.endswith((".pdf", ".docx")):
            with open(os.path.join(DOCS_DIR, filename), "rb") as f:
                text = f.read().decode(errors="ignore")
            docs.append(Document(page_content=text, metadata={"source": filename}))
    db.add_documents(docs)
    db.persist()
    print(f"Ingestion complete. {len(docs)} documents indexed into {VECTOR_STORE_DIR}")

if __name__ == "__main__":
    ingest_documents()
