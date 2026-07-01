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

### Installing and Running Ollama (Local LLM)
Since this backend uses a local AI model, you must have [Ollama](https://ollama.com/) running on your machine to use the `/query` endpoint.

**If you are a new user:**
1. Download Ollama from [ollama.com](https://ollama.com/) (or run `brew install --cask ollama` on Mac).
2. Open the Ollama application so the daemon runs in the background.
3. Open your terminal and download the required AI model:
   ```bash
   ollama pull qwen2.5:1.5b
   ```
> **Tip:** If you ever try to run `ollama serve` in your terminal and get an `address already in use` error, it simply means the Ollama application is already running happily in your background/menu bar! You can either leave it running there, or quit it from your menu bar if you specifically want to run it from the terminal.

> **⚠️ Important Note on Ollama Networking:**
> The `.env` file should have `OLLAMA_BASE_URL=http://localhost:11434`. 
> - **When running natively** (Option 1), the backend will connect to Ollama on your `localhost`.
> - **When running via Docker** (Option 2), the `docker-compose.yml` file automatically overrides this URL to `http://host.docker.internal:11434` so the container can securely route traffic to the Ollama daemon running on your host machine. You do **not** need to manually modify the `.env` file when switching between Docker and Native execution.

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
