"""
FaithLoop API - Memory (RAG) Router
"""
from fastapi import APIRouter

from api.schemas import MemorySearchRequest, MemorySearchResponse, MemorySearchHit

router = APIRouter(prefix="/memory", tags=["memory"])


@router.post("/search", response_model=MemorySearchResponse)
async def search_memory(payload: MemorySearchRequest):
    """
    메모리 검색 (stub)
    TODO: RAG similarity_search 연결
    """
    # stub: 샘플 결과 1개 반환
    stub_hit = MemorySearchHit(
        id="stub-chunk-001",
        content=f"'{payload.query}'에 대한 검색 결과 (stub)",
        score=0.85,
        meta={"source_type": "checkin", "stub": True}
    )
    
    return MemorySearchResponse(
        query=payload.query,
        hits=[stub_hit]
    )

