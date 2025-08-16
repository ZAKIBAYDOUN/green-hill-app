"""
Run locally to (re)build the vector store from your canonical docs.

Usage (PowerShell):
  $env:OPENAI_API_KEY="sk-..."
  $env:OPENAI_EMBED_MODEL="text-embedding-3-large"
  $env:GHC_DOCS_DIR="C:\\path\\to\\docs"            # folder with your strategic PDFs/DOCs
  $env:GHC_VECTOR_OUT="C:\\path\\to\\vectorstore"   # output (Chroma) directory
  python precompute_vector_store.py
"""
import os, glob
from tqdm import tqdm
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_chroma import Chroma
from pypdf import PdfReader

try:
    import docx2txt
except Exception:
    docx2txt = None

def load_docs(root: str):
    paths = []
    paths += glob.glob(os.path.join(root, "**/*.pdf"), recursive=True)
    paths += glob.glob(os.path.join(root, "**/*.docx"), recursive=True)
    docs = []
    for p in tqdm(paths, desc="Loading"):
        if p.lower().endswith(".pdf"):
            try:
                reader = PdfReader(p)
                text = "\n".join(page.extract_text() or "" for page in reader.pages)
                if text.strip():
                    docs.append(Document(page_content=text, metadata={"source": p}))
            except Exception:
                pass
        elif p.lower().endswith(".docx") and docx2txt:
            try:
                text = docx2txt.process(p) or ""
                if text.strip():
                    docs.append(Document(page_content=text, metadata={"source": p}))
            except Exception:
                pass
    return docs

def main():
    docs_dir = os.getenv("GHC_DOCS_DIR")
    out_dir = os.getenv("GHC_VECTOR_OUT")

    if not docs_dir or not os.path.isdir(docs_dir):
        raise SystemExit("Set GHC_DOCS_DIR to a folder containing your documents.")
    if not out_dir:
        raise SystemExit("Set GHC_VECTOR_OUT to the output directory for Chroma.")

    raw_docs = load_docs(docs_dir)
    splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=200)
    chunks = splitter.split_documents(raw_docs)

    embeddings = OpenAIEmbeddings(model=os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-large"))
    _ = Chroma.from_documents(chunks, embedding=embeddings, persist_directory=out_dir)
    print(f"✅ Vector store written to: {out_dir}")

if __name__ == "__main__":
    main()
