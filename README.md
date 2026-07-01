# Local RAG Backend

A completely offline, local-only Retrieval-Augmented Generation (RAG) backend built with FastAPI, LanceDB, SentenceTransformers, and Ollama.

## Architecture Highlights
- **FastAPI**: Handles high-performance asynchronous API endpoints.
- **LanceDB**: Local, embedded PyArrow-based vector database (no extra servers needed).
- **SentenceTransformers**: `BAAI/bge-small-en-v1.5` running locally via PyTorch for fast, local embedding generation.
- **Ollama**: Connects to a local Ollama instance (defaulting to `qwen2.5:1.5b`) for LLM response generation.

## Prerequisites

Before running the backend, you must initialize your local environment variables.

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
2. (Optional) Edit `.env` to configure your `OLLAMA_MODEL` and other overrides.

Make sure you have [Ollama](https://ollama.com/) running on your machine if you plan to use the `/query` endpoint.

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
> **Note:** The first time you build the Docker image, it may take 5-10 minutes because PyTorch and its CUDA drivers are downloaded.

## API Endpoints

Once running, you can access the following REST APIs:

- `GET /health`: Check if the API and LLM configurations are active.
- `POST /api/v1/ingest`: Upload a `.pdf`, `.md`, or `.html` file. The backend will parse, chunk, embed, and store it in LanceDB.
- `GET /api/v1/documents`: List all currently ingested documents in the vector store.
- `DELETE /api/v1/documents/{document_path}`: Delete a document and all of its chunks.
- `POST /api/v1/query`: Send a JSON body `{"query": "your question"}` to retrieve relevant chunks and generate a response from Ollama.

## Evaluation Pipeline

To test the latency and functionality of your RAG pipeline end-to-end:

```bash
python scripts/evaluate.py
```

This will run a suite of benchmark questions against your live API and output the average retrieval + generation latency.

## Utility Scripts

We provide cross-platform scripts in the `scripts/` directory to help automate development tasks:
- `scripts/setup.sh` / `setup.ps1`: Initializes the virtual environment, installs dependencies.
- `scripts/run.sh` / `run.ps1`: Automatically launches the Docker environment.
