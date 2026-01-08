"""
FaithLoop API - Report Router
"""
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Query

from api.schemas import WeeklyReportResponse

router = APIRouter(prefix="/report", tags=["report"])


@router.get("/weekly", response_model=WeeklyReportResponse)
async def get_weekly_report(
    week_start: Optional[str] = Query(
        default=None,
        description="주 시작일 (YYYY-MM-DD). 미입력 시 이번 주"
    )
):
    """
    주간 리포트 조회 (stub)
    TODO: 실제 체크인 데이터 기반 리포트 생성 연결
    """
    # week_start 파싱 또는 이번 주 계산
    if week_start:
        try:
            start_date = datetime.strptime(week_start, "%Y-%m-%d")
        except ValueError:
            # 파싱 실패 시 이번 주로 폴백
            today = datetime.now()
            start_date = today - timedelta(days=today.weekday())
    else:
        # 이번 주 월요일
        today = datetime.now()
        start_date = today - timedelta(days=today.weekday())
    
    # 주 종료일 (일요일)
    end_date = start_date + timedelta(days=6)
    
    return WeeklyReportResponse(
        week_start=start_date.strftime("%Y-%m-%d"),
        week_end=end_date.strftime("%Y-%m-%d"),
        summary="이번 주 체크인 데이터를 분석한 요약입니다. (stub)"
    )

