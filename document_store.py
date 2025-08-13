# document_store.py
import os
from typing import List, Optional
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain_openai import OpenAIEmbeddings

def load_documents(doc_paths: List[str]) -> List[Document]:
    """Load documents from various formats"""
    documents = []
    
    for doc_path in doc_paths:
        if not os.path.exists(doc_path):
            print(f"Warning: Document not found: {doc_path}")
            continue
            
        try:
            if doc_path.endswith('.docx'):
                # Load DOCX files
                try:
                    import docx2txt
                    text = docx2txt.process(doc_path)
                    documents.append(Document(
                        page_content=text, 
                        metadata={"source": doc_path, "type": "docx"}
                    ))
                except ImportError:
                    print("Warning: docx2txt not available, skipping .docx files")
                    
            elif doc_path.endswith('.pdf'):
                # Load PDF files
                try:
                    from pypdf import PdfReader
                    reader = PdfReader(doc_path)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text()
                    documents.append(Document(
                        page_content=text,
                        metadata={"source": doc_path, "type": "pdf"}
                    ))
                except ImportError:
                    print("Warning: pypdf not available, skipping .pdf files")
                    
            elif doc_path.endswith('.xlsx'):
                # Load Excel files
                try:
                    import pandas as pd
                    df = pd.read_excel(doc_path)
                    text = df.to_string()
                    documents.append(Document(
                        page_content=text,
                        metadata={"source": doc_path, "type": "xlsx"}
                    ))
                except ImportError:
                    print("Warning: pandas not available, skipping .xlsx files")
                    
            elif doc_path.endswith('.txt'):
                # Load text files
                with open(doc_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                documents.append(Document(
                    page_content=text,
                    metadata={"source": doc_path, "type": "txt"}
                ))
                
        except Exception as e:
            print(f"Error loading {doc_path}: {e}")
            
    return documents

def ingest_canonical_docs(doc_paths: List[str], persist_dir: str):
    """Ingest documents and create vector store"""
    print(f"Ingesting {len(doc_paths)} documents...")
    
    # Load and process documents
    documents = load_documents(doc_paths)
    if not documents:
        print("No documents loaded successfully")
        return
        
    # Split documents into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800, 
        chunk_overlap=120,
        separators=["\n\n", "\n", " ", ""]
    )
    
    docs = []
    for doc in documents:
        chunks = splitter.split_text(doc.page_content)
        for i, chunk in enumerate(chunks):
            docs.append(Document(
                page_content=chunk,
                metadata={**doc.metadata, "chunk_id": i}
            ))
    
    print(f"Created {len(docs)} document chunks")
    
    # Create embeddings and vector store
    try:
        embeddings = OpenAIEmbeddings(
            model=os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-large")
        )
        
        # Use Chroma for vector storage
        from langchain_chroma import Chroma
        
        # Ensure persist directory exists
        os.makedirs(persist_dir, exist_ok=True)
        
        vectordb = Chroma.from_documents(
            docs, 
            embedding=embeddings, 
            persist_directory=persist_dir
        )
        
        print(f"Vector store created successfully at {persist_dir}")
        return vectordb
        
    except Exception as e:
        print(f"Error creating vector store: {e}")
        return None

def get_document_store(persist_dir: str) -> Optional['Chroma']:
    """Get existing document store"""
    try:
        embeddings = OpenAIEmbeddings(
            model=os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-large")
        )
        
        from langchain_chroma import Chroma
        
        if not os.path.exists(persist_dir):
            print(f"Vector store not found at {persist_dir}")
            return None
            
        vectordb = Chroma(
            persist_directory=persist_dir, 
            embedding_function=embeddings
        )
        
        return vectordb
        
    except Exception as e:
        print(f"Error loading vector store: {e}")
        return None
