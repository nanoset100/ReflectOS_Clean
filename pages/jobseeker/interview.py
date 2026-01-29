"""
ReflectOS - 취준생 모듈: 면접 기록
면접 경험 및 질문 기록
"""
import streamlit as st
from datetime import date, datetime
from lib.auth import get_current_user
from lib.supabase_db import create_module_entry, get_module_entries

# 사용자 정보 가져오기
user = get_current_user()
user_id = user.id

st.title("💬 면접 기록")
st.caption("면접 경험과 질문을 기록하세요")

# 면접 기록 입력 폼
with st.form("interview_form", clear_on_submit=True):
    company = st.text_input(
        "회사명",
        placeholder="예: 네이버, 카카오",
        key="company"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        round_num = st.selectbox(
            "면접 차수",
            options=["1차", "2차", "3차", "최종", "기타"],
            index=0,
            key="round_num"
        )
    with col2:
        interview_date = st.date_input(
            "면접일",
            value=date.today(),
            key="interview_date"
        )
    
    interview_time = st.time_input(
        "면접 시간 (선택)",
        value=None,
        key="interview_time"
    )
    
    questions = st.text_area(
        "면접 질문",
        placeholder="질문을 하나씩 줄바꿈하여 입력하세요",
        height=150,
        key="questions"
    )
    
    self_eval = st.select_slider(
        "자기 평가",
        options=["매우 나쁨", "나쁨", "보통", "좋음", "매우 좋음"],
        value="보통",
        key="self_eval"
    )
    
    next_action = st.text_area(
        "다음 액션",
        placeholder="면접 후 해야 할 일, 개선할 점 등",
        key="next_action"
    )
    
    memo = st.text_area(
        "추가 메모",
        placeholder="특이사항, 느낀 점 등",
        key="memo"
    )
    
    submit = st.form_submit_button("💾 저장", use_container_width=True, type="primary")
    
    if submit:
        if not company.strip():
            st.error("❌ 회사명을 입력해주세요.")
        else:
            try:
                # 날짜+시간 결합
                date_time_str = None
                if interview_time:
                    dt = datetime.combine(interview_date, interview_time)
                    date_time_str = dt.isoformat()
                else:
                    date_time_str = interview_date.isoformat()
                
                # 질문을 리스트로 변환
                questions_list = [q.strip() for q in questions.split("\n") if q.strip()] if questions else []
                
                payload = {
                    "company": company,
                    "round": round_num,
                    "date_time": date_time_str,
                    "questions": questions_list,
                    "self_eval": self_eval,
                    "next_action": next_action,
                    "memo": memo
                }
                
                result = create_module_entry(
                    user_id=user_id,
                    module="jobseeker",
                    entry_type="interview",
                    occurred_on=interview_date,
                    payload=payload
                )
                
                if result:
                    st.success("✅ 면접 기록이 저장되었습니다!")
                    st.balloons()
                else:
                    st.error("❌ 저장에 실패했습니다.")
            except Exception as e:
                st.error(f"❌ 오류 발생: {e}")

# 최근 면접 기록 리스트
st.divider()
st.subheader("📋 최근 면접 기록")

try:
    interviews = get_module_entries(
        user_id=user_id,
        module="jobseeker",
        entry_type="interview",
        limit=20
    )
    
    if interviews:
        # 최신순 정렬
        interviews_sorted = sorted(
            interviews,
            key=lambda x: x.get("occurred_on", ""),
            reverse=True
        )
        
        for interview in interviews_sorted:
            occurred_on = interview.get("occurred_on", "")
            payload = interview.get("payload", {})
            
            company = payload.get("company", "")
            round_num = payload.get("round", "")
            date_time = payload.get("date_time", "")
            questions = payload.get("questions", [])
            self_eval = payload.get("self_eval", "")
            next_action = payload.get("next_action", "")
            memo = payload.get("memo", "")
            
            # 자기 평가 이모지
            eval_emoji = {
                "매우 나쁨": "😢",
                "나쁨": "😔",
                "보통": "😐",
                "좋음": "🙂",
                "매우 좋음": "😊"
            }.get(self_eval, "😐")
            
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**{company}** - {round_num}차 면접")
                    st.caption(f"📅 {occurred_on}")
                    if date_time:
                        st.caption(f"⏰ {date_time}")
                    
                    if questions:
                        with st.expander(f"❓ 면접 질문 ({len(questions)}개)"):
                            for i, q in enumerate(questions, 1):
                                st.markdown(f"{i}. {q}")
                    
                    if next_action:
                        with st.expander("📌 다음 액션"):
                            st.caption(next_action)
                    
                    if memo:
                        with st.expander("📝 메모"):
                            st.caption(memo)
                
                with col2:
                    st.markdown(f"{eval_emoji} **{self_eval}**")
                
                st.divider()
    else:
        st.info("📭 아직 면접 기록이 없습니다. 위에서 첫 기록을 남겨보세요!")
        
except Exception as e:
    st.error(f"❌ 데이터 조회 중 오류 발생: {e}")
