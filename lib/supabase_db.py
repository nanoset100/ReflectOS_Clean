"""
ReflectOS - Supabase DB CRUD 헬퍼
각 테이블별 기본 CRUD 함수 제공
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
import streamlit as st
from lib.config import get_supabase_client, get_current_user_id
from lib.utils import has_demo_tag


# ============================================
# 공통 헬퍼
# ============================================

def _get_client():
    """Supabase 클라이언트 가져오기 (내부 헬퍼)"""
    client = get_supabase_client()
    if not client:
        raise Exception("Supabase 클라이언트가 초기화되지 않았습니다.")
    return client


def _get_user_id():
    """현재 사용자 ID (내부 헬퍼)"""
    return get_current_user_id()


# ============================================
# profiles 테이블
# ============================================

def get_profile(user_id: str = None) -> Optional[Dict]:
    """사용자 프로필 조회"""
    try:
        client = _get_client()
        user_id = user_id or _get_user_id()
        
        response = client.table("profiles").select("*").eq("user_id", user_id).single().execute()
        return response.data
    except Exception as e:
        # 프로필이 없으면 None 반환
        return None


def upsert_profile(profile_data: Dict, user_id: str = None) -> Dict:
    """
    프로필 생성 또는 업데이트 (upsert)
    profile_data: {display_name, timezone, settings 등}
    """
    try:
        client = _get_client()
        user_id = user_id or _get_user_id()
        
        data = {
            "user_id": user_id,
            "updated_at": datetime.utcnow().isoformat(),
            **profile_data
        }
        
        response = client.table("profiles").upsert(data, on_conflict="user_id").execute()
        return response.data[0] if response.data else None
    except Exception as e:
        st.error(f"프로필 저장 실패: {e}")
        return None


# ============================================
# checkins 테이블
# ============================================

def insert_checkin(
    content: str,
    mood: str = "neutral",
    tags: List[str] = None,
    metadata: Dict = None,
    user_id: str = None,
    created_at: Optional[str] = None  # 데모 데이터용 옵션 인자
) -> Optional[Dict]:
    """
    새 체크인 저장
    
    Args:
        content: 체크인 내용 (텍스트)
        mood: 기분 (great/good/neutral/bad/terrible)
        tags: 태그 목록 (리스트)
        metadata: 추가 메타데이터 (energy 등)
        user_id: 사용자 ID (기본값: 현재 사용자)
        created_at: 생성 시간 (옵션, 없으면 현재 시간)
    
    Returns:
        저장된 체크인 레코드
    """
    try:
        client = _get_client()
        user_id = user_id or _get_user_id()
        
        data = {
            "user_id": user_id,
            "content": content,
            "mood": mood,
            "tags": tags or [],
            "metadata": metadata or {},
            "created_at": created_at if created_at else datetime.utcnow().isoformat()
        }
        
        response = client.table("checkins").insert(data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        st.error(f"체크인 저장 실패: {e}")
        return None


def list_checkins(
    limit: int = 10,
    offset: int = 0,
    user_id: str = None,
    exclude_demo: bool = False
) -> List[Dict]:
    """
    체크인 목록 조회 (최신순)
    
    Args:
        limit: 가져올 개수
        offset: 건너뛸 개수 (페이지네이션)
        user_id: 사용자 ID
        exclude_demo: True면 데모 데이터 제외
    
    Returns:
        체크인 레코드 목록
    """
    try:
        client = _get_client()
        user_id = user_id or _get_user_id()
        
        response = (
            client.table("checkins")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )
        
        rows = response.data or []
        if exclude_demo:
            rows = [c for c in rows if not has_demo_tag(c.get("tags", []))]
        return rows
    except Exception as e:
        st.error(f"체크인 목록 조회 실패: {e}")
        return []


def get_checkin(checkin_id: str) -> Optional[Dict]:
    """특정 체크인 조회"""
    try:
        client = _get_client()
        response = client.table("checkins").select("*").eq("id", checkin_id).single().execute()
        return response.data
    except Exception as e:
        return None


def delete_checkin(checkin_id: str) -> bool:
    """체크인 삭제"""
    try:
        client = _get_client()
        client.table("checkins").delete().eq("id", checkin_id).execute()
        return True
    except Exception as e:
        st.error(f"체크인 삭제 실패: {e}")
        return False


# ============================================
# extractions 테이블 (AI 추출 데이터)
# ============================================

def insert_extraction(
    source_type: str,
    source_id: str,
    extraction_type: str,
    data: Dict,
    user_id: str = None,
    created_at: Optional[str] = None  # 데모 데이터용 옵션 인자
) -> Optional[Dict]:
    """
    추출 데이터 저장 (규칙 기반 또는 LLM 기반)
    
    Args:
        source_type: 소스 타입 ('checkin', 'artifact', 'calendar')
        source_id: 소스 레코드 ID
        extraction_type: 추출 타입 ('rule_based', 'llm_extractor', 'keywords' 등)
        data: 추출된 데이터 (JSON)
        user_id: 사용자 ID
        created_at: 생성 시간 (옵션, 없으면 현재 시간)
    
    Returns:
        저장된 extraction 레코드
    """
    try:
        client = _get_client()
        user_id = user_id or _get_user_id()
        
        record = {
            "user_id": user_id,
            "source_type": source_type,
            "source_id": source_id,
            "extraction_type": extraction_type,
            "data": data,
            "created_at": created_at if created_at else datetime.utcnow().isoformat()
        }
        
        response = client.table("extractions").insert(record).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        st.error(f"Extraction 저장 실패: {e}")
        return None


def get_extractions_by_source(source_type: str, source_id: str) -> List[Dict]:
    """특정 소스의 모든 extraction 조회"""
    try:
        client = _get_client()
        response = (
            client.table("extractions")
            .select("*")
            .eq("source_type", source_type)
            .eq("source_id", source_id)
            .execute()
        )
        return response.data or []
    except Exception as e:
        return []


# ============================================
# artifacts 테이블 (멀티모달 첨부파일)
# ============================================

def insert_artifact(
    checkin_id: str,
    artifact_type: str,  # "image", "audio", "file"
    storage_path: str,
    metadata: Dict = None,
    original_name: str = None,
    file_size: int = None,
    user_id: str = None
) -> Optional[Dict]:
    """
    아티팩트(첨부파일) 저장
    
    Args:
        checkin_id: 연결된 체크인 ID
        artifact_type: 파일 타입 ("image", "audio", "file")
        storage_path: Supabase Storage 경로
        metadata: 추가 메타데이터 (전사 텍스트, 분석 결과 등)
        original_name: 원본 파일명
        file_size: 파일 크기 (bytes)
        user_id: 사용자 ID
    
    Returns:
        저장된 artifact 레코드
    """
    try:
        client = _get_client()
        user_id = user_id or _get_user_id()
        
        data = {
            "user_id": user_id,
            "checkin_id": checkin_id,
            "type": artifact_type,
            "storage_path": storage_path,
            "original_name": original_name,
            "file_size": file_size,
            "metadata": metadata or {},
            "created_at": datetime.utcnow().isoformat()
        }
        
        response = client.table("artifacts").insert(data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        st.error(f"아티팩트 저장 실패: {e}")
        return None


def list_artifacts_by_checkin(checkin_id: str) -> List[Dict]:
    """특정 체크인의 아티팩트 목록"""
    try:
        client = _get_client()
        response = (
            client.table("artifacts")
            .select("*")
            .eq("checkin_id", checkin_id)
            .execute()
        )
        return response.data or []
    except Exception as e:
        return []


# ============================================
# plans 테이블 (일간 플랜)
# ============================================

def upsert_plan(
    plan_date: str,  # "YYYY-MM-DD"
    plan_data: Dict = None,
    user_id: str = None
) -> Optional[Dict]:
    """일간 플랜 생성/업데이트"""
    try:
        client = _get_client()
        user_id = user_id or _get_user_id()
        
        data = {
            "user_id": user_id,
            "plan_date": plan_date,
            "updated_at": datetime.utcnow().isoformat(),
            **(plan_data or {})
        }
        
        response = client.table("plans").upsert(
            data, 
            on_conflict="user_id,plan_date"
        ).execute()
        
        return response.data[0] if response.data else None
    except Exception as e:
        st.error(f"플랜 저장 실패: {e}")
        return None


def get_plan(plan_date: str, user_id: str = None) -> Optional[Dict]:
    """특정 날짜 플랜 조회"""
    try:
        client = _get_client()
        user_id = user_id or _get_user_id()
        
        response = (
            client.table("plans")
            .select("*, plan_blocks(*)")
            .eq("user_id", user_id)
            .eq("plan_date", plan_date)
            .single()
            .execute()
        )
        return response.data
    except Exception as e:
        return None


# ============================================
# plan_blocks 테이블 (시간 블록)
# ============================================

def insert_plan_block(
    plan_id: str,
    start_time: str,  # "HH:MM"
    end_time: str,
    title: str,
    category: str = None,
    user_id: str = None
) -> Optional[Dict]:
    """시간 블록 추가"""
    try:
        client = _get_client()
        user_id = user_id or _get_user_id()
        
        data = {
            "user_id": user_id,
            "plan_id": plan_id,
            "start_time": start_time,
            "end_time": end_time,
            "title": title,
            "category": category,
            "is_completed": False
        }
        
        response = client.table("plan_blocks").insert(data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        st.error(f"블록 저장 실패: {e}")
        return None


# ============================================
# memory_chunks 테이블 (RAG용)
# ============================================

def insert_memory_chunk(
    source_type: str,  # "checkin", "note", "calendar"
    source_id: str,
    content: str,
    user_id: str = None
) -> Optional[Dict]:
    """메모리 청크 저장 (RAG 색인용)"""
    try:
        client = _get_client()
        user_id = user_id or _get_user_id()
        
        data = {
            "user_id": user_id,
            "source_type": source_type,
            "source_id": source_id,
            "content": content,
            "created_at": datetime.utcnow().isoformat()
        }
        
        response = client.table("memory_chunks").insert(data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        st.error(f"메모리 청크 저장 실패: {e}")
        return None


# ============================================
# 통계/집계 쿼리
# ============================================

def count_checkins_today(user_id: str = None) -> int:
    """오늘 체크인 횟수"""
    try:
        client = _get_client()
        user_id = user_id or _get_user_id()
        
        today = datetime.utcnow().date().isoformat()
        
        response = (
            client.table("checkins")
            .select("id", count="exact")
            .eq("user_id", user_id)
            .gte("created_at", f"{today}T00:00:00")
            .lte("created_at", f"{today}T23:59:59")
            .execute()
        )
        
        return response.count or 0
    except Exception as e:
        return 0


def get_checkins_date_range(
    start_date: str,
    end_date: str,
    user_id: str = None,
    exclude_demo: bool = False
) -> List[Dict]:
    """날짜 범위의 체크인 조회"""
    try:
        client = _get_client()
        user_id = user_id or _get_user_id()
        
        response = (
            client.table("checkins")
            .select("*")
            .eq("user_id", user_id)
            .gte("created_at", f"{start_date}T00:00:00")
            .lte("created_at", f"{end_date}T23:59:59")
            .order("created_at", desc=True)
            .execute()
        )
        
        rows = response.data or []
        if exclude_demo:
            rows = [c for c in rows if not has_demo_tag(c.get("tags", []))]
        return rows
    except Exception as e:
        return []

