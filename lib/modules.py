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
        if not isinstance(settings, dict):
            logger.warning(f"[MODULE] get_active_modules: settings가 dict가 아님: {type(settings)}. 빈 dict로 초기화.")
            settings = {}
        
        active = settings.get("active_modules", [])
        
        # active가 리스트가 아니면 빈 리스트로 초기화
        if not isinstance(active, list):
            logger.warning(f"[MODULE] get_active_modules: active_modules가 리스트가 아님: {type(active)}, {active}. 빈 리스트로 초기화.")
            active = []
        
        # 문자열이 아닌 요소 제거 및 레지스트리에 없는 모듈 제거
        valid_modules = []
        for m in active:
            if not isinstance(m, str):
                logger.warning(f"[MODULE] get_active_modules: 모듈 ID가 문자열이 아님: {type(m)}, {m}. 건너뜁니다.")
                continue
            if m in MODULE_REGISTRY:
                valid_modules.append(m)
            else:
                logger.warning(f"[MODULE] get_active_modules: 알 수 없는 모듈 ID: {m}. 건너뜁니다.")
        
        logger.info(f"[MODULE] get_active_modules: user_id={user_id}, active_modules={valid_modules}")
        return valid_modules
    except Exception as e:
        logger.error(f"[MODULE] get_active_modules 실패: user_id={user_id}, error={e}")
        # st.error는 여기서 호출하지 않음 (app.py 초기화 단계에서 호출되면 문제 발생 가능)
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
        # active가 리스트가 아니면 빈 리스트로 초기화
        if not isinstance(active, list):
            logger.warning(f"[MODULE] set_active_modules: active가 리스트가 아님: {type(active)}, {active}. 빈 리스트로 초기화.")
            active = []
        
        # 문자열이 아닌 요소 제거 및 레지스트리에 없는 모듈 제거
        valid_modules = []
        for m in active:
            if not isinstance(m, str):
                logger.warning(f"[MODULE] set_active_modules: 모듈 ID가 문자열이 아님: {type(m)}, {m}. 건너뜁니다.")
                continue
            if m in MODULE_REGISTRY:
                valid_modules.append(m)
            else:
                logger.warning(f"[MODULE] set_active_modules: 알 수 없는 모듈 ID: {m}. 건너뜁니다.")
        
        logger.info(f"[MODULE] set_active_modules 시작: user_id={user_id}, selected={active}, valid={valid_modules}")
        
        # 프로필 조회 또는 생성
        profile = get_profile(user_id=user_id)
        current_settings = (profile or {}).get("settings", {})
        
        # settings가 dict가 아니면 빈 dict로 초기화
        if not isinstance(current_settings, dict):
            logger.warning(f"[MODULE] set_active_modules: current_settings가 dict가 아님: {type(current_settings)}. 빈 dict로 초기화.")
            current_settings = {}
        
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
        try:
            get_active_modules.clear()
        except Exception as cache_error:
            logger.warning(f"[MODULE] 캐시 클리어 실패 (무시 가능): {cache_error}")
        
        logger.info(f"[MODULE] set_active_modules 성공: user_id={user_id}, saved_modules={valid_modules}")
        return True, f"저장 완료: {valid_modules}"
    except Exception as e:
        error_msg = f"활성 모듈 저장 실패: {e}"
        logger.error(f"[MODULE] set_active_modules 예외: user_id={user_id}, error={error_msg}")
        import traceback
        logger.error(f"[MODULE] 트레이스백: {traceback.format_exc()}")
        return False, error_msg
