"""
ReflectOS - 모듈 레지스트리 및 활성화 관리
"""
import streamlit as st
from typing import List
import logging
from lib.config import get_supabase_client
from lib.supabase_db import get_profile, upsert_profile

# 로깅 설정 (Streamlit Cloud 로그에 출력)
logger = logging.getLogger(__name__)

# 모듈 레지스트리 정의
MODULE_REGISTRY = {
    "health": {
        "name": "건강관리",
        "icon": "🏃",
        "description": "식단, 운동, 체중 기록"
    },
    "student": {
        "name": "수험생",
        "icon": "📚",
        "description": "학습 기록 및 관리"
    },
    "jobseeker": {
        "name": "취준생",
        "icon": "💼",
        "description": "구직 활동 기록"
    }
}


@st.cache_data(ttl=60)  # 60초 캐시 (짧게 설정하여 최신 상태 유지)
def get_active_modules(user_id: str) -> List[str]:
    """
    활성화된 모듈 목록 조회 (캐시됨)
    
    Args:
        user_id: 사용자 ID
    
    Returns:
        활성화된 모듈 ID 리스트 (예: ["health", "student"])
    """
    try:
        profile = get_profile(user_id=user_id)
        if not profile:
            logger.info(f"[MODULE] get_active_modules: user_id={user_id}, profile=None, returning []")
            return []
        
        settings = profile.get("settings", {})
        active = settings.get("active_modules", [])
        
        # 레지스트리에 없는 모듈은 제거
        valid_modules = [m for m in active if m in MODULE_REGISTRY]
        
        logger.info(f"[MODULE] get_active_modules: user_id={user_id}, active_modules={valid_modules}")
        return valid_modules
    except Exception as e:
        logger.error(f"[MODULE] get_active_modules 실패: user_id={user_id}, error={e}")
        st.error(f"활성 모듈 조회 실패: {e}")
        return []


def set_active_modules(user_id: str, active: List[str]) -> tuple[bool, str]:
    """
    활성화된 모듈 목록 저장
    
    Args:
        user_id: 사용자 ID
        active: 활성화할 모듈 ID 리스트
    
    Returns:
        (성공 여부, 메시지)
    """
    try:
        # 레지스트리에 없는 모듈은 제거
        valid_modules = [m for m in active if m in MODULE_REGISTRY]
        
        logger.info(f"[MODULE] set_active_modules 시작: user_id={user_id}, selected={active}, valid={valid_modules}")
        
        # 프로필 조회 또는 생성
        profile = get_profile(user_id=user_id)
        current_settings = (profile or {}).get("settings", {})
        
        # active_modules 업데이트
        current_settings["active_modules"] = valid_modules
        
        # 프로필 저장
        result = upsert_profile({"settings": current_settings}, user_id=user_id)
        
        if result is None:
            error_msg = "프로필 저장 실패 (result=None)"
            logger.error(f"[MODULE] set_active_modules 실패: {error_msg}")
            return False, error_msg
        
        # 캐시 클리어 (저장 직후 메뉴 갱신을 위해)
        # Settings에서도 clear하지만 여기서도 clear하여 확실히
        get_active_modules.clear()
        
        logger.info(f"[MODULE] set_active_modules 성공: user_id={user_id}, saved_modules={valid_modules}")
        return True, f"저장 완료: {valid_modules}"
    except Exception as e:
        error_msg = f"활성 모듈 저장 실패: {e}"
        logger.error(f"[MODULE] set_active_modules 예외: user_id={user_id}, error={error_msg}")
        return False, error_msg
