# Green Hill Canarias Digital Twin

How to add documents

- One-off ingestion (external files):
  - Place PDFs/DOCX/XLSX/TXT into a folder, e.g. docs/.
  - Run the ingester to build a Chroma store (HF embeddings by default):
    - python app/ingest.py --source docs --out vector_store
  - Set VECTOR_STORE_DIR=vector_store when running/deploying.

- Programmatic upserts (runtime):
  - Use the DocumentStore API exposed via the graph:
    - add_texts(texts=[...], metadatas=[...]) to add new content.
    - add_agent_outputs(state) archives agent analyses and the GreenHill memo automatically.
  - Archiving is enabled by default on finalize; disable with ARCHIVE_AGENT_OUTPUTS=0.

Environment variables

- EMBEDDING_BACKEND=hf|openai (default hf)
- HUGGINGFACE_EMBED_MODEL=sentence-transformers/all-MiniLM-L6-v2 (default)
- OPENAI_EMBED_MODEL=text-embedding-3-large (when EMBEDDING_BACKEND=openai)
- VECTOR_STORE_DIR=vector_store (path to Chroma directory)
- OPENAI_API_KEY, OPENAI_CHAT_MODEL, GREEN_HILL_CHAT_MODEL (for LLM)
- ARCHIVE_AGENT_OUTPUTS=1 (set 0 to disable auto-archiving)

Simple API and web UI

- Run the API locally:
  - pip install -r requirements.txt
  - uvicorn app.api:api --reload --host 0.0.0.0 --port 8000
- Endpoints:
  - GET /health
  - POST /api/twin/query { question, source_type }
  - POST /api/twin/ingest_texts { texts, metadatas? }
- Static UI (if running uvicorn): <http://localhost:8000/>

Cloud deployment

- The graph entrypoint is ./app/ghc_twin.py:app (see langgraph.json).
- Dependencies include langchain-huggingface and sentence-transformers for HF embeddings.# green-hill-app

