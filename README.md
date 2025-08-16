# green-hill-app

This repository contains the Green Hill Club application.

## Optional dependencies

The core app does not require additional libraries.  Utilities for working with the
vector store (see `document_store.py` and `precompute_vector_store.py`) rely on the
LangChain ecosystem and other helpers.  To enable these features, install the
optional packages listed in [`requirements.txt`](requirements.txt):

```
pip install -r requirements.txt
```

These dependencies include `langchain-openai`, `langchain-chroma`, `langchain-text-splitters`, `pypdf`, `tqdm`, and `docx2txt`.

