# 004 - Embeddings

**Decision:** Use `BAAI/bge-small-en-v1.5` via `Sentence Transformers`.

**Alternatives:** OpenAI embeddings, local `all-MiniLM-L6-v2`.

**Why chosen:** Required by constraints. It provides excellent retrieval performance for a small model size and runs completely locally.

**Tradeoffs:** Slower than API-based embeddings unless run on a GPU, and adds significant weight to the backend image if model weights are baked in (we will dynamically download/cache them).
