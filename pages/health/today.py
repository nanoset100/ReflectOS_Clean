"""
ReflectOS - 건강 모듈: 오늘 기록
식단/운동/체중 기록 페이지
"""
import streamlit as st
from datetime import date
from lib.auth import get_current_user
from lib.supabase_db import create_module_entry

# 사용자 정보 가져오기
user = get_current_user()
user_id = user.id

st.title("📝 오늘 기록")
st.caption("식단, 운동, 체중을 기록하세요")

# 탭 구성
tab1, tab2, tab3 = st.tabs(["🍽️ 식단", "🏋️ 운동", "⚖️ 체중"])

# ========================================
# 식단 탭
# ========================================
with tab1:
    st.subheader("🍽️ 식단 기록")
    
    with st.form("meal_form", clear_on_submit=True):
        meal_date = st.date_input("날짜", value=date.today(), key="meal_date")
        meal_type = st.selectbox(
            "식사 종류",
            options=["아침", "점심", "저녁", "간식"],
            key="meal_type"
        )
        meal_content = st.text_area(
            "식단 내용",
            placeholder="예: 밥, 된장국, 김치, 계란후라이",
            key="meal_content"
        )
        meal_calories = st.number_input(
            "칼로리 (kcal)",
            min_value=0,
            value=0,
            step=50,
            key="meal_calories"
        )
        
        meal_submit = st.form_submit_button("💾 저장", use_container_width=True, type="primary")
        
        if meal_submit:
            if not meal_content.strip():
                st.error("❌ 식단 내용을 입력해주세요.")
            else:
                try:
                    payload = {
                        "meal_type": meal_type,
                        "content": meal_content,
                        "calories": meal_calories
                    }
                    
                    result = create_module_entry(
                        user_id=user_id,
                        module="health",
                        entry_type="meal",
                        occurred_on=meal_date,
                        payload=payload
                    )
                    
                    if result:
                        st.success("✅ 식단이 기록되었습니다!")
                        st.balloons()
                    else:
                        st.error("❌ 저장에 실패했습니다.")
                except Exception as e:
                    st.error(f"❌ 오류 발생: {e}")

# ========================================
# 운동 탭
# ========================================
with tab2:
    st.subheader("🏋️ 운동 기록")
    
    with st.form("exercise_form", clear_on_submit=True):
        exercise_date = st.date_input("날짜", value=date.today(), key="exercise_date")
        exercise_type = st.text_input(
            "운동 종류",
            placeholder="예: 러닝, 헬스, 수영, 요가",
            key="exercise_type"
        )
        exercise_duration = st.number_input(
            "운동 시간 (분)",
            min_value=0,
            value=30,
            step=5,
            key="exercise_duration"
        )
        exercise_intensity = st.select_slider(
            "운동 강도",
            options=["낮음", "보통", "높음", "매우 높음"],
            value="보통",
            key="exercise_intensity"
        )
        exercise_notes = st.text_area(
            "메모",
            placeholder="예: 5km 달리기 완료, 컨디션 좋음",
            key="exercise_notes"
        )
        
        exercise_submit = st.form_submit_button("💾 저장", use_container_width=True, type="primary")
        
        if exercise_submit:
            if not exercise_type.strip():
                st.error("❌ 운동 종류를 입력해주세요.")
            else:
                try:
                    payload = {
                        "exercise_type": exercise_type,
                        "duration": exercise_duration,
                        "intensity": exercise_intensity,
                        "notes": exercise_notes
                    }
                    
                    result = create_module_entry(
                        user_id=user_id,
                        module="health",
                        entry_type="exercise",
                        occurred_on=exercise_date,
                        payload=payload
                    )
                    
                    if result:
                        st.success("✅ 운동이 기록되었습니다!")
                        st.balloons()
                    else:
                        st.error("❌ 저장에 실패했습니다.")
                except Exception as e:
                    st.error(f"❌ 오류 발생: {e}")

# ========================================
# 체중 탭
# ========================================
with tab3:
    st.subheader("⚖️ 체중 기록")
    
    with st.form("weight_form", clear_on_submit=True):
        weight_date = st.date_input("날짜", value=date.today(), key="weight_date")
        weight_value = st.number_input(
            "체중 (kg)",
            min_value=0.0,
            value=70.0,
            step=0.1,
            format="%.1f",
            key="weight_value"
        )
        body_fat = st.number_input(
            "체지방률 (%)",
            min_value=0.0,
            value=0.0,
            step=0.1,
            format="%.1f",
            key="body_fat"
        )
        muscle_mass = st.number_input(
            "골격근량 (kg)",
            min_value=0.0,
            value=0.0,
            step=0.1,
            format="%.1f",
            key="muscle_mass"
        )
        weight_notes = st.text_area(
            "메모",
            placeholder="예: 아침 공복 측정",
            key="weight_notes"
        )
        
        weight_submit = st.form_submit_button("💾 저장", use_container_width=True, type="primary")
        
        if weight_submit:
            try:
                payload = {
                    "weight": weight_value,
                    "body_fat": body_fat if body_fat > 0 else None,
                    "muscle_mass": muscle_mass if muscle_mass > 0 else None,
                    "notes": weight_notes
                }
                
                result = create_module_entry(
                    user_id=user_id,
                    module="health",
                    entry_type="weight",
                    occurred_on=weight_date,
                    payload=payload
                )
                
                if result:
                    st.success("✅ 체중이 기록되었습니다!")
                    st.balloons()
                else:
                    st.error("❌ 저장에 실패했습니다.")
            except Exception as e:
                st.error(f"❌ 오류 발생: {e}")
