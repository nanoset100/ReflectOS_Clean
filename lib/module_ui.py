"""
ReflectOS - 모듈 UI 공통 렌더링 헬퍼
모듈별 기록 요약 표시를 위한 공통 함수
"""
import streamlit as st
from typing import Dict, List


def render_module_entry_summary(entry: Dict) -> str:
    """
    모듈 엔트리를 간단한 요약 텍스트로 변환
    
    Args:
        entry: module_entries 레코드
    
    Returns:
        요약 텍스트
    """
    entry_type = entry.get("entry_type", "")
    payload = entry.get("payload", {})
    module = entry.get("module", "")
    
    # 모듈별/타입별 요약 생성
    if module == "health":
        if entry_type == "meal":
            return f"{payload.get('meal_type', '')}: {payload.get('content', '')}"
        elif entry_type == "exercise":
            return f"{payload.get('exercise_type', '')} {payload.get('duration', 0)}분"
        elif entry_type == "weight":
            return f"{payload.get('weight', 0)}kg"
    
    elif module == "student":
        if entry_type == "study_session":
            subject = payload.get("subject", "")
            duration = payload.get("duration_min", 0)
            return f"{subject} {duration}분"
        elif entry_type == "subject_plan":
            subject = payload.get("subject", "")
            target = payload.get("weekly_target_min", 0)
            return f"{subject} (주 {target}분 목표)"
        elif entry_type == "slump_log":
            mood = payload.get("mood", "")
            trigger = payload.get("trigger", "")
            return f"{mood}: {trigger[:30]}..." if trigger else mood
    
    elif module == "jobseeker":
        if entry_type == "application":
            company = payload.get("company", "")
            role = payload.get("role", "")
            status = payload.get("status", "")
            return f"{company} - {role} ({status})"
        elif entry_type == "interview":
            company = payload.get("company", "")
            round_num = payload.get("round", "")
            return f"{company} {round_num}차 면접"
        elif entry_type == "resume":
            title = payload.get("title", "")
            version = payload.get("version", "")
            return f"{title} (v{version})" if version else title
    
    # 기본: payload의 주요 키 표시
    if payload:
        # 첫 번째 키-값 쌍 표시
        keys = list(payload.keys())[:2]
        parts = [f"{k}: {payload.get(k)}" for k in keys if payload.get(k)]
        return " | ".join(parts) if parts else str(payload)[:50]
    
    return "기록 없음"


def get_entry_type_icon(entry_type: str, module: str) -> str:
    """
    entry_type에 따른 아이콘 반환
    
    Args:
        entry_type: 엔트리 타입
        module: 모듈 ID
    
    Returns:
        이모지 아이콘
    """
    # 건강 모듈
    if module == "health":
        icons = {
            "meal": "🍽️",
            "exercise": "🏋️",
            "weight": "⚖️"
        }
        return icons.get(entry_type, "📝")
    
    # 수험생 모듈
    elif module == "student":
        icons = {
            "study_session": "📖",
            "subject_plan": "📋",
            "slump_log": "😔"
        }
        return icons.get(entry_type, "📚")
    
    # 취준생 모듈
    elif module == "jobseeker":
        icons = {
            "application": "📮",
            "interview": "💬",
            "resume": "📄"
        }
        return icons.get(entry_type, "💼")
    
    return "📝"


def render_module_summary_section(
    module_id: str,
    module_info: Dict,
    recent_entries: List[Dict]
):
    """
    모듈별 요약 섹션 렌더링
    
    Args:
        module_id: 모듈 ID
        module_info: MODULE_REGISTRY의 모듈 정보
        recent_entries: 최근 기록 리스트
    """
    st.markdown(f"### {module_info['icon']} {module_info['name']}")
    
    if recent_entries:
        for entry in recent_entries:
            occurred_on = entry.get("occurred_on", "")
            entry_type = entry.get("entry_type", "")
            module = entry.get("module", module_id)
            
            icon = get_entry_type_icon(entry_type, module)
            content = render_module_entry_summary(entry)
            
            col1, col2 = st.columns([1, 4])
            with col1:
                st.markdown(f"### {icon}")
                st.caption(occurred_on)
            with col2:
                st.markdown(content)
        
        if len(recent_entries) >= 3:
            st.caption(f"더 보려면 {module_info['name']} 메뉴를 확인하세요.")
    else:
        st.caption(f"아직 기록이 없습니다. **{module_info['name']}** 페이지에서 첫 기록을 남겨보세요!")
