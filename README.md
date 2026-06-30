# RAG Backend

A production-ready Retrieval-Augmented Generation (RAG) backend built for local environments.

## Features (In Progress)
- Local embeddings (SentenceTransformers)
- Vector Storage (LanceDB)
- API (FastAPI)
- Local LLM Integration (Ollama)

## Getting Started

### Option 1: Run Locally (Recommended for Development)
To run natively on your host machine with hot-reloading:

```bash
# 1. Activate the virtual environment
source .venv/bin/activate

# 2. Run the development server
uvicorn app.main:app --reload
```
The server will be available at `http://localhost:8000`. You can view the interactive API documentation at `http://localhost:8000/docs`.

### Option 2: Run via Docker
To run inside a fully isolated Linux container:

```bash
docker compose up --build
```
> **Note:** The first time you build the Docker image, it may take 5-10 minutes. This is because PyTorch (and its NVIDIA CUDA drivers) are over 2GB and must be downloaded from scratch into the Linux environment. Subsequent starts will be almost instant!

The server will be available at `http://localhost:8000/docs`.
