import os
from typing import Optional, List
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

# ENV:
# OPENAI_API_KEY (required)
# OPENAI_EMBED_MODEL (default: text-embedding-3-large)
# GHC_VECTOR_DIR -> path to a persistent Chroma directory (mounted/available in deploy)

def get_vectorstore(persist_dir: str) -> Chroma:
    embed_model = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-large")
    embeddings = OpenAIEmbeddings(model=embed_model)
    return Chroma(persist_directory=persist_dir, embedding_function=embeddings)

def get_retriever(top_k: int = 6):
    persist_dir = os.getenv("GHC_VECTOR_DIR")
    if not persist_dir or not os.path.isdir(persist_dir):
        # No vector store mounted — return a harmless retriever that yields nothing
        class _Empty:
            def get_relevant_documents(self, *_args, **_kwargs) -> List:
                return []
        return _Empty()
    return get_vectorstore(persist_dir).as_retriever(search_kwargs={"k": top_k})
