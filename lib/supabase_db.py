"""
ReflectOS - Supabase DB CRUD 헬퍼
각 테이블별 기본 CRUD 함수 제공
"""
from datetime import datetime, date
from typing import Optional, List, Dict, Any, Tuple
import streamlit as st
from lib.config import get_supabase_client, get_current_user_id
from lib.utils import has_demo_tag


# ============================================
# 공통 헬퍼
# ============================================

def _get_client():
    """
    Supabase 클라이언트 가져오기 (내부 헬퍼)
    토큰 만료 시 자동으로 로그아웃 처리
    """
    client = get_supabase_client()
    if not client:
        raise Exception("Supabase 클라이언트가 초기화되지 않았습니다.")
    return client


def _is_pgrst205_error(e: Exception) -> bool:
    """
    PGRST205 오류 감지 (테이블이 schema cache에 없음)
    
    Returns:
        PGRST205 오류인지 여부
    """
    error_str = str(e)
    error_code = getattr(e, 'code', None)
    
    # PGRST205 코드 확인
    if error_code == "PGRST205":
        return True
    
    # 메시지 패턴 확인
    if "PGRST205" in error_str:
        return True
    
    # schema cache + module_entries 패턴 확인
    if "schema cache" in error_str.lower() and "module_entries" in error_str.lower():
        return True
    
    return False


def _handle_pgrst205_error():
    """
    PGRST205 오류 발생 시 친절한 안내 메시지 표시
    """
    st.error("""
    ❌ **데이터베이스 테이블이 설정되지 않았습니다**
    
    **해결 방법:**
    
    1. Supabase SQL Editor에서 다음 파일을 순서대로 실행하세요:
       - `sql/module_entries.sql`
       - `sql/reload_pgrst_schema.sql`
    
    2. 실행 후 Streamlit 앱을 새로고침하거나 재시작하세요.
    
    3. 여전히 오류가 발생하면 Settings 페이지의 "DB 상태 확인" 버튼을 사용하세요.
    """)
    
    # 페이지 크래시 방지: 빈 리스트 반환 (호출부에서 처리)
    return None


def _handle_auth_error(e: Exception):
    """
    인증 관련 오류 처리 (401, 권한 거부 등)
    토큰 만료 시 로그아웃 처리
    """
    error_msg = str(e).lower()
    
    # PGRST205 오류는 별도 처리
    if _is_pgrst205_error(e):
        _handle_pgrst205_error()
        return
    
    # 401 Unauthorized 또는 권한 관련 오류 감지
    if "401" in error_msg or "unauthorized" in error_msg or "permission denied" in error_msg or "row-level security" in error_msg:
        try:
            from lib.auth import logout
            logout()
            st.warning("⚠️ 세션이 만료되었습니다. 다시 로그인해주세요.")
            st.rerun()
        except:
            pass


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
        # 인증 오류 처리
        _handle_auth_error(e)
        # 프로필이 없으면 None 반환
        return None


def upsert_profile(profile_data: Dict, user_id: str = None) -> Dict:
    """
    프로필 생성 또는 업데이트 (upsert)
    profile_data: {display_name, timezone, settings 등}
    
    주의: 이 함수는 로그인 후에만 호출되어야 함 (RLS 정책)
    """
    try:
        client = _get_client()
        user_id = user_id or _get_user_id()
        
        if not user_id:
            st.error("사용자 ID가 없습니다. 로그인이 필요합니다.")
            return None
        
        data = {
            "user_id": user_id,
            "updated_at": datetime.utcnow().isoformat(),
            **profile_data
        }
        
        response = client.table("profiles").upsert(data, on_conflict="user_id").execute()
        return response.data[0] if response.data else None
    except Exception as e:
        # 인증 오류 처리
        _handle_auth_error(e)
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
        _handle_auth_error(e)
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
        _handle_auth_error(e)
        st.error(f"체크인 목록 조회 실패: {e}")
        return []


def get_checkin(checkin_id: str, user_id: str = None) -> Optional[Dict]:
    """특정 체크인 조회"""
    try:
        client = _get_client()
        user_id = user_id or _get_user_id()
        
        query = client.table("checkins").select("*").eq("id", checkin_id)
        if user_id:
            query = query.eq("user_id", user_id)
        
        response = query.single().execute()
        return response.data
    except Exception as e:
        return None


def delete_checkin(checkin_id: str, user_id: str = None) -> bool:
    """체크인 삭제"""
    try:
        client = _get_client()
        user_id = user_id or _get_user_id()
        
        query = client.table("checkins").delete().eq("id", checkin_id)
        if user_id:
            query = query.eq("user_id", user_id)
        
        query.execute()
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


def get_extractions_by_source(source_type: str, source_id: str, user_id: str = None) -> List[Dict]:
    """특정 소스의 모든 extraction 조회"""
    try:
        client = _get_client()
        user_id = user_id or _get_user_id()
        
        query = (
            client.table("extractions")
            .select("*")
            .eq("source_type", source_type)
            .eq("source_id", source_id)
        )
        if user_id:
            query = query.eq("user_id", user_id)
        
        response = query.execute()
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


def list_artifacts_by_checkin(checkin_id: str, user_id: str = None) -> List[Dict]:
    """특정 체크인의 아티팩트 목록"""
    try:
        client = _get_client()
        user_id = user_id or _get_user_id()
        
        query = (
            client.table("artifacts")
            .select("*")
            .eq("checkin_id", checkin_id)
        )
        if user_id:
            query = query.eq("user_id", user_id)
        
        response = query.execute()
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


# ============================================
# module_entries 테이블 (공용 모듈 데이터)
# ============================================

def create_module_entry(
    user_id: str,
    module: str,
    entry_type: str,
    occurred_on: date,
    payload: Dict,
    tags: List[str] = None,
    metadata: Dict = None
) -> Optional[Dict]:
    """
    모듈 엔트리 생성
    
    Args:
        user_id: 사용자 ID (반드시 auth uid 문자열이어야 함, 이메일 금지)
        module: 모듈 ID ('health', 'student', 'jobseeker')
        entry_type: 엔트리 타입 (예: 'meal', 'exercise', 'weight')
        occurred_on: 발생 날짜
        payload: 데이터 (JSONB)
        tags: 태그 리스트
        metadata: 메타데이터 (JSONB)
    
    Returns:
        생성된 엔트리 레코드
    """
    try:
        client = _get_client()
        
        # user_id 검증 (이메일이 아닌 auth uid인지 확인)
        if "@" in user_id:
            st.error("❌ user_id는 이메일이 아닌 auth uid 문자열이어야 합니다.")
            return None
        
        data = {
            "user_id": user_id,  # auth uid 문자열 (RLS 정책과 일치)
            "module": module,
            "entry_type": entry_type,
            "occurred_on": occurred_on.isoformat() if isinstance(occurred_on, date) else occurred_on,
            "payload": payload or {},
            "tags": tags or [],
            "metadata": metadata or {}
        }
        
        response = client.table("module_entries").insert(data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        # PGRST205 오류 처리
        if _is_pgrst205_error(e):
            _handle_pgrst205_error()
            return None
        
        # 인증 오류 처리
        _handle_auth_error(e)
        st.error(f"모듈 엔트리 생성 실패: {e}")
        return None


def get_module_entries(
    user_id: str,
    module: str = None,
    entry_type: str = None,
    limit: int = 10,
    date_range: Tuple[date, date] = None
) -> List[Dict]:
    """
    모듈 엔트리 목록 조회
    
    Args:
        user_id: 사용자 ID (반드시 auth uid 문자열이어야 함)
        module: 모듈 필터 (선택)
        entry_type: 엔트리 타입 필터 (선택)
        limit: 최대 개수
        date_range: 날짜 범위 (start_date, end_date) 튜플 (선택)
    
    Returns:
        엔트리 레코드 목록 (최신순)
    """
    try:
        client = _get_client()
        
        query = client.table("module_entries").select("*").eq("user_id", user_id)
        
        # 모듈 필터
        if module:
            query = query.eq("module", module)
        
        # 엔트리 타입 필터
        if entry_type:
            query = query.eq("entry_type", entry_type)
        
        # 날짜 범위 필터
        if date_range:
            start_date, end_date = date_range
            query = query.gte("occurred_on", start_date.isoformat())
            query = query.lte("occurred_on", end_date.isoformat())
        
        # 정렬 및 제한
        response = (
            query
            .order("occurred_on", desc=True)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        
        return response.data or []
    except Exception as e:
        # PGRST205 오류 처리
        if _is_pgrst205_error(e):
            _handle_pgrst205_error()
            return []  # 빈 리스트 반환하여 페이지 크래시 방지
        
        # 인증 오류 처리
        _handle_auth_error(e)
        st.error(f"모듈 엔트리 조회 실패: {e}")
        return []

