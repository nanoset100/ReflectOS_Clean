"""
ReflectOS - 수험생 모듈: 슬럼프 로그
학습 슬럼프 기록 및 관리
"""
import streamlit as st
from datetime import date
from lib.auth import get_current_user
from lib.supabase_db import create_module_entry, get_module_entries

# 사용자 정보 가져오기
user = get_current_user()
user_id = user.id

st.title("😔 슬럼프 로그")
st.caption("학습 슬럼프를 기록하고 극복 방법을 찾아보세요")

# 슬럼프 로그 입력 폼
with st.form("slump_log_form", clear_on_submit=True):
    slump_date = st.date_input("날짜", value=date.today(), key="slump_date")
    
    mood = st.selectbox(
        "기분",
        options=["매우 나쁨", "나쁨", "보통", "좋음", "매우 좋음"],
        index=1,
        key="mood"
    )
    
    trigger = st.text_area(
        "슬럼프 원인/계기",
        placeholder="예: 시험 결과가 나쁨, 특정 과목이 어려움, 피로 누적 등",
        key="trigger"
    )
    
    symptoms = st.text_area(
        "증상/느낌",
        placeholder="예: 집중이 안 됨, 공부하기 싫음, 불안감 등",
        key="symptoms"
    )
    
    action = st.text_area(
        "시도한 대처 방법",
        placeholder="예: 휴식, 운동, 친구와 대화 등",
        key="action"
    )
    
    result = st.selectbox(
        "결과",
        options=["개선됨", "조금 나아짐", "변화 없음", "더 나빠짐"],
        index=1,
        key="result"
    )
    
    memo = st.text_area(
        "추가 메모",
        placeholder="느낀 점, 다음에 시도할 것 등",
        key="memo"
    )
    
    submit = st.form_submit_button("💾 저장", use_container_width=True, type="primary")
    
    if submit:
        if not trigger.strip():
            st.error("❌ 슬럼프 원인을 입력해주세요.")
        else:
            try:
                payload = {
                    "mood": mood,
                    "trigger": trigger,
                    "symptoms": symptoms,
                    "action": action,
                    "result": result,
                    "memo": memo
                }
                
                result_entry = create_module_entry(
                    user_id=user_id,
                    module="student",
                    entry_type="slump_log",
                    occurred_on=slump_date,
                    payload=payload
                )
                
                if result_entry:
                    st.success("✅ 슬럼프 로그가 저장되었습니다!")
                    st.balloons()
                    st.info("💡 슬럼프는 누구에게나 찾아옵니다. 기록을 통해 패턴을 발견하고 극복해나가세요!")
                else:
                    st.error("❌ 저장에 실패했습니다.")
            except Exception as e:
                st.error(f"❌ 오류 발생: {e}")

# 최근 5개 슬럼프 로그 표시
st.divider()
st.subheader("📋 최근 슬럼프 로그")

try:
    slump_logs = get_module_entries(
        user_id=user_id,
        module="student",
        entry_type="slump_log",
        limit=5
    )
    
    if slump_logs:
        for log in slump_logs:
            occurred_on = log.get("occurred_on", "")
            payload = log.get("payload", {})
            
            mood = payload.get("mood", "")
            trigger = payload.get("trigger", "")
            symptoms = payload.get("symptoms", "")
            action = payload.get("action", "")
            result = payload.get("result", "")
            memo = payload.get("memo", "")
            
            # 기분별 이모지
            mood_emoji = {
                "매우 나쁨": "😢",
                "나쁨": "😔",
                "보통": "😐",
                "좋음": "🙂",
                "매우 좋음": "😊"
            }.get(mood, "😐")
            
            # 결과별 색상
            result_colors = {
                "개선됨": "🟢",
                "조금 나아짐": "🟡",
                "변화 없음": "⚪",
                "더 나빠짐": "🔴"
            }
            result_icon = result_colors.get(result, "⚪")
            
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**{mood_emoji} {mood}**")
                    st.caption(f"📅 {occurred_on}")
                    
                    if trigger:
                        with st.expander("🔍 원인/계기"):
                            st.caption(trigger)
                    
                    if symptoms:
                        with st.expander("💭 증상/느낌"):
                            st.caption(symptoms)
                    
                    if action:
                        with st.expander("💪 대처 방법"):
                            st.caption(action)
                    
                    if memo:
                        with st.expander("📝 메모"):
                            st.caption(memo)
                
                with col2:
                    st.markdown(f"{result_icon} **{result}**")
                
                st.divider()
    else:
        st.info("📭 아직 슬럼프 로그가 없습니다. 위에서 첫 기록을 남겨보세요!")
        
except Exception as e:
    st.error(f"❌ 데이터 조회 중 오류 발생: {e}")
