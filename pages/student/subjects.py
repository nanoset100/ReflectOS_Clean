"""
ReflectOS - 수험생 모듈: 과목 목표 관리
과목별 학습 목표 설정 및 관리
"""
import streamlit as st
from datetime import date
from lib.auth import get_current_user
from lib.supabase_db import create_module_entry, get_module_entries

# 사용자 정보 가져오기
user = get_current_user()
user_id = user.id

st.title("📋 과목 목표")
st.caption("과목별 학습 목표를 설정하고 관리하세요")

# 과목 목표 입력 폼
with st.form("subject_plan_form", clear_on_submit=True):
    subject = st.text_input(
        "과목",
        placeholder="예: 수학, 영어, 국어",
        key="subject"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        weekly_target_min = st.number_input(
            "주간 목표 시간 (분)",
            min_value=0,
            value=300,
            step=30,
            key="weekly_target_min"
        )
    with col2:
        priority = st.selectbox(
            "우선순위",
            options=["높음", "보통", "낮음"],
            index=1,
            key="priority"
        )
    
    exam_date = st.date_input(
        "시험일 (선택)",
        value=None,
        key="exam_date"
    )
    
    memo = st.text_area(
        "메모",
        placeholder="과목별 특이사항, 학습 전략 등",
        key="memo"
    )
    
    submit = st.form_submit_button("💾 저장", use_container_width=True, type="primary")
    
    if submit:
        if not subject.strip():
            st.error("❌ 과목을 입력해주세요.")
        else:
            try:
                payload = {
                    "subject": subject,
                    "weekly_target_min": weekly_target_min,
                    "priority": priority,
                    "exam_date": exam_date.isoformat() if exam_date else None,
                    "memo": memo
                }
                
                result = create_module_entry(
                    user_id=user_id,
                    module="student",
                    entry_type="subject_plan",
                    occurred_on=date.today(),  # 목표 설정일
                    payload=payload
                )
                
                if result:
                    st.success("✅ 과목 목표가 저장되었습니다!")
                    st.balloons()
                else:
                    st.error("❌ 저장에 실패했습니다.")
            except Exception as e:
                st.error(f"❌ 오류 발생: {e}")

# 과목 목표 리스트 표시
st.divider()
st.subheader("📊 과목 목표 목록")

try:
    subject_plans = get_module_entries(
        user_id=user_id,
        module="student",
        entry_type="subject_plan",
        limit=20
    )
    
    if subject_plans:
        # 최신순 정렬
        subject_plans_sorted = sorted(
            subject_plans,
            key=lambda x: x.get("created_at", ""),
            reverse=True
        )
        
        for plan in subject_plans_sorted:
            payload = plan.get("payload", {})
            created_at = plan.get("created_at", "")[:10]
            
            subject = payload.get("subject", "")
            weekly_target = payload.get("weekly_target_min", 0)
            priority = payload.get("priority", "보통")
            exam_date = payload.get("exam_date", "")
            memo = payload.get("memo", "")
            
            # 우선순위별 색상
            priority_colors = {
                "높음": "🔴",
                "보통": "🟡",
                "낮음": "🟢"
            }
            priority_icon = priority_colors.get(priority, "⚪")
            
            with st.container():
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    st.markdown(f"**{subject}**")
                    st.caption(f"설정일: {created_at}")
                
                with col2:
                    st.markdown(f"주간 목표: {weekly_target}분")
                    if exam_date:
                        st.caption(f"시험일: {exam_date}")
                
                with col3:
                    st.markdown(f"{priority_icon} {priority}")
                
                if memo:
                    with st.expander("📝 메모"):
                        st.caption(memo)
                
                st.divider()
    else:
        st.info("📭 아직 과목 목표가 없습니다. 위에서 첫 목표를 설정해보세요!")
        
except Exception as e:
    st.error(f"❌ 데이터 조회 중 오류 발생: {e}")
