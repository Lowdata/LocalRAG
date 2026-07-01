# Local RAG Backend

A completely offline, local-only Retrieval-Augmented Generation (RAG) backend built with FastAPI, LanceDB, SentenceTransformers, and Ollama.

## Architecture

This project is divided into two primary parts:

1. **Part 1: Cost Efficient RAG**
   - A fast, deterministic retrieval pipeline leveraging LanceDB as a low-cost, high-performance embedded store.
   - Intelligent chunking that respects whitespace boundaries.
   - Built-in strict IR metrics (Recall@k, nDCG, Context Precision) using deterministic chunk IDs.

2. **Part 2: Evaluation Framework**
   - An extensible "LLM-as-a-Judge" grading pipeline that evaluates generated RAG answers for Correctness, Faithfulness, and Completeness.
   - Includes robust bias-checking modules (position bias, verbosity, sycophancy).
   - Generates auditable suite reports with full prompt/response logging.

## Setup & Run Instructions

Anyone on our team can clone and run this in under ~10 minutes. 

### Prerequisites
- **Runtime:** Python 3.10+
- **OS:** macOS (Apple Silicon/Intel) or Linux (Ubuntu 20.04+)
- **Services:** [Ollama](https://ollama.com/) (must be running in the background)
- **Hardware:** Apple Silicon (M1+) or 8GB+ RAM (CPU only is supported but slower).

### Environment Variables
*(Copy from `.env.example` to `.env`)*
- `OLLAMA_BASE_URL`
- `OLLAMA_MODEL`
- `EMBEDDING_MODEL`
- `VECTOR_STORE_PATH`
- `LOG_LEVEL`
- `JUDGE_MODEL`

### Install
```bash
# 1. Clone the repository
git clone https://github.com/your-org/LocalRAG.git
cd LocalRAG

# 2. Setup virtual environment
python -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Pull the required models via Ollama
ollama pull qwen2.5:1.5b
ollama pull llama3.2

# 5. Initialize environment variables
cp .env.example .env

# 6. Start the FastAPI server
uvicorn app.main:app --reload
```

### Ingest a corpus
Upload a document to the vector store. By default, the system uses a **chunk size of 512** tokens and an **overlap of 50** tokens.
```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/ingest' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@docs/architecture.md'
```

### Run a query
Ask a question over your ingested corpus.
```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/query' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "query": "What is the weak link in the architecture?",
  "document_path": "docs/architecture.md"
}'
```

## API Endpoints

Once running, you can access the following REST APIs:

- `GET /health`: Check if the API and LLM configurations are active.
- `POST /api/v1/ingest`: Upload a `.pdf`, `.md`, or `.html` file. The backend will parse, chunk, embed, and store it in LanceDB.
- `GET /api/v1/documents`: List all currently ingested documents in the vector store.
- `DELETE /api/v1/documents/{document_path}`: Delete a document and all of its chunks.
- `POST /api/v1/query`: Send a JSON body `{"query": "your question"}` to retrieve relevant chunks and generate a response from Ollama.

## Evaluation Pipelines

### 1. IR Evaluation (Retrieval + Generation Metrics)
To test the strict latency and IR metrics of your RAG pipeline end-to-end (Retrieval Hit Rate, MRR, Context Precision, Recall@k):

```bash
python scripts/evaluate_ir.py
```

This will run a suite of benchmark questions against your live API and output the average retrieval + generation latency alongside real IR metrics.

### 2. LLM-as-a-Judge Framework
To run the full grading pipeline that evaluates generated RAG answers for Correctness, Faithfulness, and Completeness:

```bash
python scripts/evaluate_judge.py
```
This script will:
1. Load cases from `eval_datasets/judge/suite.json`.
2. Hit your local `/query` API to generate a real answer.
3. Feed the generated answer, expected answer, and question into the Ollama Judge model.
4. Output a comprehensive suite report in `reports/judge/`.

You can also test the Judge endpoints manually in Swagger (`http://localhost:8000/docs#/Judge`).

### Weak Links (Retrieval vs. Generation)
Based on our benchmarking:
- Average end-to-end latency: **~1.02 s**
- Average retrieval latency (LanceDB): **~20 ms**
- Average generation latency (Qwen 2.5): **~1000 ms**

Retrieval therefore contributes **<2%** of total latency while generation contributes **>98%**. Optimizing the vector store provides marginal speed gains, highly justifying the massive cost savings of our embedded DB choice.

> **Read more in our complete [Infrastructure Cost Analysis](docs/cost_analysis.md).**

## Utility Scripts

We provide cross-platform scripts in the `scripts/` directory to help automate development tasks:
- `scripts/setup.sh` / `setup.ps1`: Initializes the virtual environment, installs dependencies.
- `scripts/run.sh` / `run.ps1`: Automatically launches the Docker environment.
