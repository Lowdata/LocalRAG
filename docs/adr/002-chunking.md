# 002 - Document Chunking

**Decision:** Implement a custom chunker instead of using LangChain splitters.

**Alternatives:** LangChain `RecursiveCharacterTextSplitter`.

**Why chosen:** Explicitly mandated by the user constraints to avoid LangChain abstractions and demonstrate core software engineering skills.

**Tradeoffs:** Requires writing our own logic for overlapping characters and boundaries, increasing development time but providing full control over implementation details.
