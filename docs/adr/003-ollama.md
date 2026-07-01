# 003 - LLM Engine

**Decision:** Use Ollama running natively on the host machine.

**Alternatives:** Dockerized Ollama, OpenAI API, local huggingface pipelines.

**Why chosen:** Constrained by the requirement for a fully local system without paid APIs. Running on the host machine instead of docker allows easier access to GPU acceleration without complex nvidia-docker configurations in a portable setup.

**Tradeoffs:** The host must have Ollama installed and running the `qwen2.5:1.5b` (generator) and `llama3.2` (judge) models prior to using the backend. 
