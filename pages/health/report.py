"""
ReflectOS - 건강 모듈: 건강 리포트
최근 7일 요약 (체중 변화, 운동 횟수, 식단 기록 횟수)
"""
import streamlit as st
from datetime import date, timedelta
from lib.auth import get_current_user
from lib.supabase_db import get_module_entries

# 사용자 정보 가져오기
user = get_current_user()
user_id = user.id

st.title("📈 건강 리포트")
st.caption("최근 7일 건강 기록 요약")

# 날짜 범위 설정
end_date = date.today()
start_date = end_date - timedelta(days=7)

try:
    # 각 타입별 데이터 조회
    weight_entries = get_module_entries(
        user_id=user_id,
        module="health",
        entry_type="weight",
        date_range=(start_date, end_date),
        limit=100
    )
    
    exercise_entries = get_module_entries(
        user_id=user_id,
        module="health",
        entry_type="exercise",
        date_range=(start_date, end_date),
        limit=100
    )
    
    meal_entries = get_module_entries(
        user_id=user_id,
        module="health",
        entry_type="meal",
        date_range=(start_date, end_date),
        limit=100
    )
    
    # ========================================
    # 체중 변화 분석
    # ========================================
    st.subheader("⚖️ 체중 변화")
    
    if weight_entries:
        # 날짜순 정렬
        weight_sorted = sorted(weight_entries, key=lambda x: x.get("occurred_on", ""))
        
        if len(weight_sorted) >= 2:
            first_weight = weight_sorted[0].get("payload", {}).get("weight", 0)
            last_weight = weight_sorted[-1].get("payload", {}).get("weight", 0)
            change = last_weight - first_weight
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("시작 체중", f"{first_weight:.1f} kg")
            with col2:
                st.metric("현재 체중", f"{last_weight:.1f} kg")
            with col3:
                st.metric("변화량", f"{change:+.1f} kg", delta=f"{change:+.1f} kg")
        else:
            current_weight = weight_sorted[0].get("payload", {}).get("weight", 0)
            st.metric("현재 체중", f"{current_weight:.1f} kg")
            st.caption("변화량을 계산하려면 최소 2회 이상 기록이 필요합니다.")
    else:
        st.info("📭 체중 기록이 없습니다.")
    
    st.divider()
    
    # ========================================
    # 운동 통계
    # ========================================
    st.subheader("🏋️ 운동 통계")
    
    if exercise_entries:
        total_duration = sum(e.get("payload", {}).get("duration", 0) for e in exercise_entries)
        exercise_count = len(exercise_entries)
        avg_duration = total_duration / exercise_count if exercise_count > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("운동 횟수", f"{exercise_count}회")
        with col2:
            st.metric("총 운동 시간", f"{total_duration}분")
        with col3:
            st.metric("평균 운동 시간", f"{avg_duration:.0f}분")
        
        # 운동 종류별 통계
        exercise_types = {}
        for entry in exercise_entries:
            ex_type = entry.get("payload", {}).get("exercise_type", "기타")
            exercise_types[ex_type] = exercise_types.get(ex_type, 0) + 1
        
        if exercise_types:
            st.caption("운동 종류별 횟수:")
            for ex_type, count in sorted(exercise_types.items(), key=lambda x: x[1], reverse=True):
                st.caption(f"  • {ex_type}: {count}회")
    else:
        st.info("📭 운동 기록이 없습니다.")
    
    st.divider()
    
    # ========================================
    # 식단 통계
    # ========================================
    st.subheader("🍽️ 식단 통계")
    
    if meal_entries:
        meal_count = len(meal_entries)
        total_calories = sum(e.get("payload", {}).get("calories", 0) for e in meal_entries)
        avg_calories = total_calories / meal_count if meal_count > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("식사 기록", f"{meal_count}회")
        with col2:
            st.metric("총 칼로리", f"{total_calories:.0f} kcal")
        with col3:
            st.metric("평균 칼로리", f"{avg_calories:.0f} kcal")
        
        # 식사 종류별 통계
        meal_types = {}
        for entry in meal_entries:
            meal_type = entry.get("payload", {}).get("meal_type", "기타")
            meal_types[meal_type] = meal_types.get(meal_type, 0) + 1
        
        if meal_types:
            st.caption("식사 종류별 횟수:")
            for meal_type, count in sorted(meal_types.items(), key=lambda x: x[1], reverse=True):
                st.caption(f"  • {meal_type}: {count}회")
    else:
        st.info("📭 식단 기록이 없습니다.")
    
    st.divider()
    
    # ========================================
    # 종합 평가
    # ========================================
    st.subheader("💡 종합 평가")
    
    score = 0
    feedback = []
    
    if weight_entries:
        score += 1
        feedback.append("✅ 체중 기록이 있습니다")
    else:
        feedback.append("⚠️ 체중 기록이 없습니다")
    
    if exercise_entries:
        score += 1
        feedback.append("✅ 운동 기록이 있습니다")
    else:
        feedback.append("⚠️ 운동 기록이 없습니다")
    
    if meal_entries:
        score += 1
        feedback.append("✅ 식단 기록이 있습니다")
    else:
        feedback.append("⚠️ 식단 기록이 없습니다")
    
    for item in feedback:
        st.caption(item)
    
    if score == 3:
        st.success("🎉 완벽합니다! 모든 항목을 기록하고 계시네요!")
    elif score == 2:
        st.info("👍 좋습니다! 조금만 더 기록하면 완벽해요!")
    elif score == 1:
        st.warning("💪 조금만 더 노력하면 좋은 습관이 될 거예요!")
    else:
        st.info("📝 오늘부터 건강 기록을 시작해보세요!")
        
except Exception as e:
    st.error(f"❌ 리포트 생성 중 오류 발생: {e}")
