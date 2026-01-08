"""
FaithLoop API - Checkins Router
"""
import uuid
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter

from api.schemas import CheckinCreate, CheckinOut

router = APIRouter(prefix="/checkins", tags=["checkins"])


@router.post("", response_model=CheckinOut)
async def create_checkin(payload: CheckinCreate):
    """
    체크인 생성 (stub)
    TODO: Supabase insert 연결
    """
    checkin_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc)
    
    return CheckinOut(
        id=checkin_id,
        text=payload.text,
        created_at=created_at,
        source=payload.source
    )


@router.get("", response_model=List[CheckinOut])
async def list_checkins():
    """
    체크인 목록 조회 (stub)
    TODO: Supabase select 연결
    """
    return []

