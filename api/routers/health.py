"""
FaithLoop API - Health Router
"""
from fastapi import APIRouter

from api.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """헬스체크 엔드포인트"""
    return HealthResponse(ok=True)

