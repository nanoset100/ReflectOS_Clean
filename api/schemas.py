"""
FaithLoop API - Pydantic 스키마 정의
"""
from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field


# ============================================================
# Checkin 관련 스키마
# ============================================================

class CheckinCreate(BaseModel):
    """체크인 생성 요청"""
    text: str = Field(..., min_length=1, description="체크인 내용")
    source: str = Field(default="api", description="체크인 소스 (api, web, mobile)")


class CheckinOut(BaseModel):
    """체크인 응답"""
    id: str = Field(..., description="체크인 UUID")
    text: str = Field(..., description="체크인 내용")
    created_at: datetime = Field(..., description="생성 시간 (UTC)")
    source: Optional[str] = Field(default=None, description="체크인 소스")


# ============================================================
# Memory (RAG) 관련 스키마
# ============================================================

class MemorySearchRequest(BaseModel):
    """메모리 검색 요청"""
    query: str = Field(..., min_length=1, description="검색 쿼리")
    top_k: int = Field(default=8, ge=1, le=50, description="반환할 결과 수")


class MemorySearchHit(BaseModel):
    """메모리 검색 결과 항목"""
    id: str = Field(..., description="청크 ID")
    content: str = Field(..., description="청크 내용")
    score: float = Field(..., description="유사도 점수 (0~1)")
    meta: Optional[dict] = Field(default=None, description="메타데이터")


class MemorySearchResponse(BaseModel):
    """메모리 검색 응답"""
    query: str = Field(..., description="검색 쿼리")
    hits: List[MemorySearchHit] = Field(default_factory=list, description="검색 결과")


# ============================================================
# Report 관련 스키마
# ============================================================

class WeeklyReportResponse(BaseModel):
    """주간 리포트 응답"""
    week_start: str = Field(..., description="주 시작일 (YYYY-MM-DD)")
    week_end: str = Field(..., description="주 종료일 (YYYY-MM-DD)")
    summary: str = Field(..., description="주간 요약")


# ============================================================
# Health 관련 스키마
# ============================================================

class HealthResponse(BaseModel):
    """헬스체크 응답"""
    ok: bool = Field(default=True)

