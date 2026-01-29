"""
ReflectOS - 수험생 모듈: 오늘 학습 기록
학습 세션 기록 페이지
"""
import streamlit as st
from datetime import date
from lib.auth import get_current_user
from lib.supabase_db import create_module_entry, get_module_entries

# 사용자 정보 가져오기
user = get_current_user()
user_id = user.id

st.title("📖 오늘 학습")
st.caption("학습 세션을 기록하세요")

# 학습 세션 입력 폼
with st.form("study_session_form", clear_on_submit=True):
    study_date = st.date_input("날짜", value=date.today(), key="study_date")
    
    subject = st.text_input(
        "과목",
        placeholder="예: 수학, 영어, 국어",
        key="subject"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        duration_min = st.number_input(
            "학습 시간 (분)",
            min_value=0,
            value=60,
            step=5,
            key="duration_min"
        )
    with col2:
        focus = st.slider(
            "집중도 (1~5)",
            min_value=1,
            max_value=5,
            value=3,
            help="1: 매우 낮음 ~ 5: 매우 높음",
            key="focus"
        )
    
    topics = st.text_input(
        "학습 주제 (쉼표로 구분)",
        placeholder="예: 함수, 미적분, 삼각함수",
        key="topics"
    )
    
    memo = st.text_area(
        "메모",
        placeholder="오늘 배운 점, 어려웠던 부분, 다음에 할 일 등",
        key="memo"
    )
    
    submit = st.form_submit_button("💾 저장", use_container_width=True, type="primary")
    
    if submit:
        if not subject.strip():
            st.error("❌ 과목을 입력해주세요.")
        else:
            try:
                # topics를 리스트로 변환
                topics_list = [t.strip() for t in topics.split(",") if t.strip()] if topics else []
                
                # tags 생성: ["학습", subject]
                tags = ["학습", subject]
                
                payload = {
                    "subject": subject,
                    "duration_min": duration_min,
                    "topics": topics_list,
                    "focus": focus,
                    "memo": memo
                }
                
                result = create_module_entry(
                    user_id=user_id,
                    module="student",
                    entry_type="study_session",
                    occurred_on=study_date,
                    payload=payload,
                    tags=tags
                )
                
                if result:
                    st.success("✅ 학습 세션이 기록되었습니다!")
                    st.balloons()
                else:
                    st.error("❌ 저장에 실패했습니다.")
            except Exception as e:
                st.error(f"❌ 오류 발생: {e}")

# 최근 5개 학습 세션 표시
st.divider()
st.subheader("📚 최근 학습 세션")

try:
    recent_sessions = get_module_entries(
        user_id=user_id,
        module="student",
        entry_type="study_session",
        limit=5
    )
    
    if recent_sessions:
        for session in recent_sessions:
            occurred_on = session.get("occurred_on", "")
            payload = session.get("payload", {})
            
            subject = payload.get("subject", "")
            duration = payload.get("duration_min", 0)
            focus = payload.get("focus", 0)
            topics = payload.get("topics", [])
            memo = payload.get("memo", "")
            
            with st.container():
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**{subject}** - {duration}분")
                    st.caption(f"📅 {occurred_on}")
                    
                    if topics:
                        st.caption(f"주제: {', '.join(topics)}")
                    
                    if memo:
                        with st.expander("📝 메모"):
                            st.caption(memo)
                
                with col2:
                    # 집중도 표시
                    focus_stars = "⭐" * focus
                    st.markdown(f"집중도: {focus_stars}")
                
                st.divider()
    else:
        st.info("📭 아직 학습 세션이 없습니다. 위에서 첫 기록을 남겨보세요!")
        
except Exception as e:
    st.error(f"❌ 데이터 조회 중 오류 발생: {e}")
