# RAG Infrastructure Cost Analysis

This document evaluates the cost, latency, and operational trade-offs of deploying our self-hosted RAG pipeline (LanceDB + FastAPI) versus utilizing a fully managed vector database like Pinecone.

## Objective
On a fully managed vector DB, billing often scales with stored vectors or always-on pod sizes. For applications with large but lightly-queried indexes, this can result in high, inflexible infrastructure costs. We benchmarked a low-cost embedded alternative (LanceDB).

## Choice of Store: LanceDB
We selected **LanceDB** for this project. 
- **Reasoning:** It is an open-source, embedded vector database designed to run in-process or serverless. It uses a columnar data format (Lance) based on PyArrow, offering high performance for analytical queries and vector search without requiring a dedicated server or network overhead. It writes directly to the disk, meaning storage scales exactly with standard NVMe disk space rather than expensive managed RAM.

## Cost Comparison Table
*Assuming 1 Vector = 384 dimensions (BAAI/bge-small-en-v1.5), approx 1.5 KB per vector with metadata.*

| Scale (Vectors) | Estimated Size | Self-Hosted LanceDB (AWS EC2 / EBS) | Managed Pinecone (Standard) | Managed Qdrant Cloud |
|-----------------|----------------|-------------------------------------|-----------------------------|----------------------|
| **100,000**     | ~150 MB        | **$5/mo** (t3.nano, 8GB EBS)        | **$0/mo** (Starter Tier)    | **$0/mo** (Free Tier)|
| **1,000,000**   | ~1.5 GB        | **$5/mo** (t3.nano, 8GB EBS)        | **$70/mo** (1 x1 pod)       | **$25/mo** (1GB RAM) |
| **10,000,000**  | ~15 GB         | **$12/mo** (t3.micro, 20GB EBS)     | **$140/mo** (2 x1 pods)     | **$100/mo** (4GB RAM)|

### Infrastructure Breakdown (Self-Hosted)
- Our LanceDB index sits entirely on the local disk.
- At 10M vectors, the index takes ~15GB. AWS EBS charges ~$0.08 per GB/mo ($1.20/mo for storage).
- The compute overhead for a lightly-queried internal tool is negligible, allowing it to run on a t3.micro ($10.51/mo).
- Total cost for 10M vectors is under $15/mo, compared to $100-$140/mo on managed providers.

## Trade-offs & Discussion

### When to switch back to a Managed DB?
While LanceDB is exceptionally cheap and fast for single-node deployments, you should switch back to a managed provider (like Pinecone or Qdrant Cloud) when:
1. **High Concurrency / Distributed Scaling:** If you need to scale FastAPI across dozens of stateless Kubernetes pods, maintaining a single source of truth for an embedded disk-based DB becomes complex (requires NFS/EFS or LanceDB Enterprise).
2. **Operational Overhead:** If managing EBS volumes, backups, and EC2 uptime detracts from engineering velocity.
3. **Advanced Filtering:** Managed DBs offer highly optimized pre-filtering on complex JSON metadata schemas that might outperform local naive filtering.

### Weak Links (Retrieval vs. Generation)
Based on our latency benchmarking (`p50` and `p95`):
- **Retrieval is NOT the bottleneck.** LanceDB returns top-k nearest neighbors in less than 20ms. PyTorch `bge-small` embedding takes ~100ms.
- **Generation is the weak link.** The LLM step (Ollama `qwen2.5:1.5b`) consumes 95% of the total request latency, usually taking 2,000ms - 5,000ms depending on Apple Silicon GPU acceleration.
- Therefore, optimizing the vector store provides marginal user-experience gains. The massive cost savings of an embedded DB are highly justified since they do not negatively impact the true bottleneck (the LLM).
