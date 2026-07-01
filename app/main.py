import typing
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.middleware.logging import log_requests
from app.core.config import settings
from app.api.endpoints import storage, query, judge

app = FastAPI(title="Local RAG Backend")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(storage.router, prefix="/api/v1", tags=["Storage"])
app.include_router(query.router, prefix="/api/v1", tags=["Query"])
app.include_router(judge.router, prefix="/api/v1/judge", tags=["Judge"])

app.middleware("http")(log_requests)


@app.get("/health", tags=["System"])
async def health_check() -> typing.Dict[str, str]:
    return {"status": "healthy", "model": settings.ollama_model}
