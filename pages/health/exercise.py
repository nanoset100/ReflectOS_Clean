"""
ReflectOS - 건강 모듈: 운동 기록 목록
운동 로그 리스트 출력
"""
import streamlit as st
from datetime import date, timedelta
from lib.auth import get_current_user
from lib.supabase_db import get_module_entries

# 사용자 정보 가져오기
user = get_current_user()
user_id = user.id

st.title("🏋️ 운동 기록")
st.caption("운동 로그를 확인하세요")

# 날짜 범위 선택
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("시작일", value=date.today() - timedelta(days=7))
with col2:
    end_date = st.date_input("종료일", value=date.today())

# 운동 데이터 조회
try:
    entries = get_module_entries(
        user_id=user_id,
        module="health",
        entry_type="exercise",
        date_range=(start_date, end_date),
        limit=100
    )
    
    if not entries:
        st.info("📭 선택한 기간에 운동 기록이 없습니다. **오늘 기록** 페이지에서 첫 기록을 남겨보세요!")
    else:
        # 최신순 정렬
        entries_sorted = sorted(entries, key=lambda x: x.get("occurred_on", ""), reverse=True)
        
        st.subheader(f"운동 기록 ({len(entries_sorted)}개)")
        
        for entry in entries_sorted:
            occurred_on = entry.get("occurred_on", "")
            payload = entry.get("payload", {})
            
            exercise_type = payload.get("exercise_type", "운동")
            duration = payload.get("duration", 0)
            intensity = payload.get("intensity", "보통")
            notes = payload.get("notes", "")
            
            # 강도별 이모지
            intensity_emoji = {
                "낮음": "🟢",
                "보통": "🟡",
                "높음": "🟠",
                "매우 높음": "🔴"
            }.get(intensity, "⚪")
            
            with st.container():
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    st.markdown(f"**{exercise_type}**")
                    st.caption(f"📅 {occurred_on}")
                
                with col2:
                    st.markdown(f"⏱️ {duration}분")
                    st.caption(f"{intensity_emoji} {intensity}")
                
                with col3:
                    if notes:
                        with st.expander("📝 메모"):
                            st.caption(notes)
                
                st.divider()
        
        # 통계 요약
        st.subheader("📊 요약")
        total_duration = sum(e.get("payload", {}).get("duration", 0) for e in entries_sorted)
        exercise_types = {}
        for entry in entries_sorted:
            ex_type = entry.get("payload", {}).get("exercise_type", "기타")
            exercise_types[ex_type] = exercise_types.get(ex_type, 0) + 1
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("총 운동 시간", f"{total_duration}분")
        with col2:
            st.metric("운동 종류", f"{len(exercise_types)}가지")
        
        if exercise_types:
            st.caption("운동 종류별 횟수:")
            for ex_type, count in sorted(exercise_types.items(), key=lambda x: x[1], reverse=True):
                st.caption(f"  • {ex_type}: {count}회")
            
except Exception as e:
    st.error(f"❌ 데이터 조회 중 오류 발생: {e}")
