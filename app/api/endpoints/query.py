from fastapi import APIRouter, HTTPException, Depends
from app.schemas.api import QueryRequest, QueryResponse, SourceChunk
from app.storage.vector_store import VectorStore
from app.services.llm_service import LLMService

router = APIRouter()


def get_vector_store() -> VectorStore:
    return VectorStore()


@router.post("/query", response_model=QueryResponse)
async def query_documents(
    request: QueryRequest, store: VectorStore = Depends(get_vector_store)
) -> QueryResponse:
    try:
        # 1. Retrieve
        results = store.search(
            request.query, limit=request.top_k, document_path=request.document_path
        )

        # 2. Extract Context and Sources
        context_texts = []
        sources = []
        for r in results:
            context_texts.append(r.text)
            sources.append(
                SourceChunk(
                    chunk_id=r.chunk_id,
                    document_path=r.document_path,
                    page_number=r.page_number,
                    text=r.text,
                )
            )

        # 3. Formulate Prompt
        prompt = LLMService.build_prompt(request.query, context_texts)

        # 4. Query LLM
        answer = await LLMService.generate_response(prompt)

        return QueryResponse(answer=answer, sources=sources)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during query: {str(e)}")
