# Local RAG Backend

A completely offline, local-only Retrieval-Augmented Generation (RAG) backend built with FastAPI, LanceDB, SentenceTransformers, and Ollama.

**📺 [Watch the full Walkthrough Video on Loom](https://www.loom.com/share/35e1b27a3a2c470e8f2526639a31e53e)**

## Architecture

This project is divided into two primary parts:

1. **Part 1: Cost Efficient RAG**
   - A fast, deterministic retrieval pipeline leveraging LanceDB as a low-cost, high-performance embedded store.
   - Intelligent chunking that respects whitespace boundaries.
   - Built-in strict IR metrics (Recall@k, nDCG, Context Precision) using deterministic chunk IDs.

2. **Part 2: Evaluation Framework (LLM-as-a-Judge)**
   - An extensible "LLM-as-a-Judge" grading pipeline that evaluates generated RAG answers against a ground-truth dataset.
   - Designed with strict cross-family judging (**Qwen 2.5:1.5b** as Generator, **Llama 3.2** as Judge) to mitigate self-enhancement bias.
   - Implements robust bias-checking modules, including a mathematical A/B swap to eradicate Position Bias.
   - Handles structured JSON parsing with regex fallbacks to gracefully recover from judge hallucinations.

## Setup & Run Instructions

Anyone on our team can clone and run this in under ~10 minutes. 

### Prerequisites
- **Runtime:** Python 3.10+
- **OS:** macOS (Apple Silicon/Intel) or Linux (Ubuntu 20.04+)
- **Services:** [Ollama](https://ollama.com/) (must be installed and running in the background)
- **Hardware:** Apple Silicon (M1+) or 8GB+ RAM.

### Install & Start
```bash
# 1. Clone the repository
git clone https://github.com/Lowdata/LocalRAG.git
cd ragproject

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

# 6. Start the FastAPI server (Runs on port 8000)
uvicorn app.main:app --reload
```

## API Endpoints

Once running, you can access the interactive Swagger UI at `http://localhost:8000/docs`.

- `GET /health`: Check if the API and LLM configurations are active.
- `POST /api/v1/ingest`: Upload a `.pdf`, `.md`, or `.html` file. The backend will parse, chunk, embed, and store it in LanceDB.
- `GET /api/v1/documents`: List all currently ingested documents in the vector store.
- `POST /api/v1/query`: Send a JSON body `{"query": "your question"}` to retrieve relevant chunks and generate a response from Ollama.
- `POST /api/v1/judge`: Manually test the LLM judge pipeline on a single case.

## Evaluation Pipelines

### 1. Full LLM-as-a-Judge Suite
To run the full grading pipeline that evaluates generated RAG answers for Correctness, Faithfulness, and Completeness:

```bash
python run_synthetic_eval.py
```
This script will:
1. Load cases from `eval_dataset.json`.
2. Hit the local `/query` API to generate a real answer using **Qwen**.
3. Feed the generated answer, expected answer, and question into the **Llama 3.2** Judge model.
4. Catch and parse the structured JSON verdict (with regex fallbacks for trailing characters).
5. Output a comprehensive suite report.

### 2. Position Bias Adversarial Probe
To run our dedicated script that mathematically proves Llama 3.2 grades actual content and not just the order in which answers are presented (A/B swap):

```bash
python test_position_bias.py
```
This feeds Answer A and Answer B, and then swaps them, ensuring a 0% flip-rate. All evaluations and raw Llama 3.2 outputs are logged locally to `logs/judge_audit.jsonl` for full auditability.

## Infrastructure Insights
Based on our benchmarking:
- **End-to-end latency:** ~3.2 seconds
- **Retrieval latency (LanceDB):** ~18 ms
- **Generation latency (Qwen 1.5b):** ~3100 ms

Retrieval therefore contributes **<1%** of total latency while generation contributes **>99%**. Optimizing the vector store provides marginal speed gains, highly justifying the massive cost savings of our embedded DB choice ($0.12/mo vs $2.33/mo for managed cloud stores).

> **Read more in our complete [Infrastructure Cost Analysis](docs/cost_analysis.md).**
