"""
FaithLoop API - FastAPI 메인 엔트리포인트
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import health, checkins, memory, report

# FastAPI 앱 생성
app = FastAPI(
    title="FaithLoop API",
    description="FaithLoop (ReflectOS 파생) RAG 개인화 도구 API",
    version="0.1.0",
)

# CORS 설정 (개발용 전체 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(health.router)              # /health
app.include_router(checkins.router)            # /checkins
app.include_router(memory.router)              # /memory
app.include_router(report.router)              # /report


@app.get("/")
async def root():
    """루트 엔드포인트 - API 정보"""
    return {
        "name": "FaithLoop API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health"
    }

