import typing
from fastapi import FastAPI
from app.middleware.logging import log_requests
from app.core.config import settings
from app.api.endpoints import storage

app = FastAPI(title="RAG Backend API", version="0.1.0")
app.include_router(storage.router, prefix="/api/v1", tags=["Storage"])

app.middleware("http")(log_requests)


@app.get("/health", tags=["System"])
async def health_check() -> typing.Dict[str, str]:
    return {"status": "healthy", "model": settings.ollama_model}
