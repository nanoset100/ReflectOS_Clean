"""
ReflectOS - 모듈 레지스트리 및 활성화 관리
"""
import streamlit as st
from typing import List
from lib.config import get_supabase_client
from lib.supabase_db import get_profile, upsert_profile


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


def get_active_modules(user_id: str) -> List[str]:
    """
    활성화된 모듈 목록 조회
    
    Args:
        user_id: 사용자 ID
    
    Returns:
        활성화된 모듈 ID 리스트 (예: ["health", "student"])
    """
    try:
        profile = get_profile(user_id=user_id)
        if not profile:
            return []
        
        settings = profile.get("settings", {})
        active = settings.get("active_modules", [])
        
        # 레지스트리에 없는 모듈은 제거
        valid_modules = [m for m in active if m in MODULE_REGISTRY]
        
        return valid_modules
    except Exception as e:
        st.error(f"활성 모듈 조회 실패: {e}")
        return []


def set_active_modules(user_id: str, active: List[str]) -> bool:
    """
    활성화된 모듈 목록 저장
    
    Args:
        user_id: 사용자 ID
        active: 활성화할 모듈 ID 리스트
    
    Returns:
        성공 여부
    """
    try:
        # 레지스트리에 없는 모듈은 제거
        valid_modules = [m for m in active if m in MODULE_REGISTRY]
        
        # 프로필 조회 또는 생성
        profile = get_profile(user_id=user_id)
        current_settings = (profile or {}).get("settings", {})
        
        # active_modules 업데이트
        current_settings["active_modules"] = valid_modules
        
        # 프로필 저장
        result = upsert_profile({"settings": current_settings}, user_id=user_id)
        
        return result is not None
    except Exception as e:
        st.error(f"활성 모듈 저장 실패: {e}")
        return False
