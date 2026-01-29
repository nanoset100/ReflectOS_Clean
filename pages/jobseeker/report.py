"""
ReflectOS - 취준생 모듈: 취준 리포트
최근 7일 지원 현황 및 통계
"""
import streamlit as st
from datetime import date, timedelta
from lib.auth import get_current_user
from lib.supabase_db import get_module_entries

# 사용자 정보 가져오기
user = get_current_user()
user_id = user.id

st.title("📊 취준 리포트")
st.caption("최근 7일 지원 현황 요약")

# 날짜 범위 설정
end_date = date.today()
start_date = end_date - timedelta(days=7)

try:
    # 지원 정보 조회
    applications = get_module_entries(
        user_id=user_id,
        module="jobseeker",
        entry_type="application",
        date_range=(start_date, end_date),
        limit=100
    )
    
    # 면접 기록 조회
    interviews = get_module_entries(
        user_id=user_id,
        module="jobseeker",
        entry_type="interview",
        date_range=(start_date, end_date),
        limit=100
    )
    
    # ========================================
    # 지원 현황 집계
    # ========================================
    st.subheader("📮 지원 현황")
    
    if not applications:
        st.info("📭 최근 7일간 지원 기록이 없습니다.")
    else:
        # 상태별 집계
        status_counts = {}
        for app in applications:
            status = app.get("payload", {}).get("status", "기타")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("전체 지원", f"{len(applications)}건")
        with col2:
            st.metric("지원 완료", f"{status_counts.get('지원 완료', 0)}건")
        with col3:
            st.metric("서류 통과", f"{status_counts.get('서류 통과', 0)}건")
        with col4:
            st.metric("면접 진행", f"{status_counts.get('면접 진행', 0)}건")
        with col5:
            st.metric("최종 합격", f"{status_counts.get('최종 합격', 0)}건")
        
        # 상태별 분포 차트
        if status_counts:
            import pandas as pd
            
            status_data = {
                "상태": list(status_counts.keys()),
                "건수": list(status_counts.values())
            }
            df_status = pd.DataFrame(status_data)
            st.bar_chart(df_status.set_index("상태"))
    
    st.divider()
    
    # ========================================
    # 면접 통계
    # ========================================
    st.subheader("💬 면접 통계")
    
    if not interviews:
        st.info("📭 최근 7일간 면접 기록이 없습니다.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("면접 횟수", f"{len(interviews)}회")
        with col2:
            # 회사별 면접 횟수
            company_interviews = {}
            for interview in interviews:
                company = interview.get("payload", {}).get("company", "기타")
                company_interviews[company] = company_interviews.get(company, 0) + 1
            
            unique_companies = len(company_interviews)
            st.metric("면접 회사 수", f"{unique_companies}개")
        
        # 회사별 면접 분포
        if company_interviews:
            st.caption("회사별 면접 횟수:")
            for company, count in sorted(company_interviews.items(), key=lambda x: x[1], reverse=True):
                st.caption(f"  • {company}: {count}회")
    
    st.divider()
    
    # ========================================
    # 다음 액션 Top 3
    # ========================================
    st.subheader("📌 다음 액션 Top 3")
    
    # 면접에서 next_action 추출
    next_actions = []
    for interview in interviews:
        action = interview.get("payload", {}).get("next_action", "")
        if action and action.strip():
            next_actions.append(action.strip())
    
    if next_actions:
        # 중복 제거 후 상위 3개
        unique_actions = list(dict.fromkeys(next_actions))[:3]
        
        for i, action in enumerate(unique_actions, 1):
            st.markdown(f"{i}. {action}")
    else:
        st.caption("기록된 다음 액션이 없습니다.")
    
    st.divider()
    
    # ========================================
    # 종합 평가
    # ========================================
    st.subheader("💡 종합 평가")
    
    score = 0
    feedback = []
    
    if applications:
        score += 1
        feedback.append("✅ 지원 활동이 활발합니다")
    else:
        feedback.append("⚠️ 지원 활동이 부족합니다")
    
    if status_counts.get("서류 통과", 0) > 0:
        score += 1
        feedback.append("✅ 서류 통과가 있습니다")
    else:
        feedback.append("⚠️ 서류 통과가 없습니다")
    
    if interviews:
        score += 1
        feedback.append("✅ 면접 경험이 있습니다")
    else:
        feedback.append("⚠️ 면접 기록이 없습니다")
    
    for item in feedback:
        st.caption(item)
    
    if score == 3:
        st.success("🎉 완벽합니다! 지원 활동이 활발하네요!")
    elif score == 2:
        st.info("👍 좋습니다! 조금만 더 노력하면 완벽해요!")
    elif score == 1:
        st.warning("💪 조금만 더 노력하면 좋은 결과가 있을 거예요!")
    else:
        st.info("📝 오늘부터 지원 활동을 시작해보세요!")
        
except Exception as e:
    st.error(f"❌ 리포트 생성 중 오류 발생: {e}")
