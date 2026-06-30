# 001 - Vector Database

**Decision:** Use LanceDB.

**Alternatives:** Pinecone, Weaviate, Milvus, Chroma.

**Why chosen:** LanceDB runs completely locally without requiring cloud infrastructure, aligns with the fully local constraints, and performs well for both embeddings and metadata filtering.

**Tradeoffs:** Does not have some of the massive distributed scaling capabilities of managed databases, but easily meets the requirement of an interview assignment with reproducibility.
