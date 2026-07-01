from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Server configuration
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"

    # Document Processing
    chunk_size: int = 500
    chunk_overlap: int = 50

    # LLM configuration
    ollama_model: str = "qwen2.5:1.5b"
    generator_model: str = "qwen2.5:1.5b"
    judge_model: str = "llama3.2"
    judge_prompt: str = "v1"
    ollama_base_url: str = "http://host.docker.internal:11434"

    # Vector DB
    vector_db_path: str = "data/lancedb"

    # Embeddings
    embedding_model: str = "BAAI/bge-small-en-v1.5"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
