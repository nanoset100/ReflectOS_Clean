"""
ReflectOS - 수험생 모듈: 학습 리포트
최근 7일 학습 통계 및 분석
"""
import streamlit as st
from datetime import date, timedelta
from lib.auth import get_current_user
from lib.supabase_db import get_module_entries

# 사용자 정보 가져오기
user = get_current_user()
user_id = user.id

st.title("📊 학습 리포트")
st.caption("최근 7일 학습 통계를 확인하세요")

# 날짜 범위 설정
end_date = date.today()
start_date = end_date - timedelta(days=7)

try:
    # 학습 세션 데이터 조회
    study_sessions = get_module_entries(
        user_id=user_id,
        module="student",
        entry_type="study_session",
        date_range=(start_date, end_date),
        limit=100
    )
    
    if not study_sessions:
        st.info("📭 최근 7일간 학습 기록이 없습니다.")
    else:
        # ========================================
        # 총 학습 시간
        # ========================================
        total_minutes = sum(s.get("payload", {}).get("duration_min", 0) for s in study_sessions)
        total_hours = total_minutes / 60
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("총 학습 시간", f"{total_hours:.1f}시간", f"{total_minutes}분")
        with col2:
            st.metric("학습 세션 수", f"{len(study_sessions)}회")
        with col3:
            avg_minutes = total_minutes / len(study_sessions) if study_sessions else 0
            st.metric("평균 세션 시간", f"{avg_minutes:.0f}분")
        
        st.divider()
        
        # ========================================
        # 과목별 분포
        # ========================================
        st.subheader("📚 과목별 학습 시간")
        
        subject_times = {}
        for session in study_sessions:
            subject = session.get("payload", {}).get("subject", "기타")
            duration = session.get("payload", {}).get("duration_min", 0)
            subject_times[subject] = subject_times.get(subject, 0) + duration
        
        if subject_times:
            # 과목별 시간을 시간 단위로 변환하여 표시
            for subject, minutes in sorted(subject_times.items(), key=lambda x: x[1], reverse=True):
                hours = minutes / 60
                percentage = (minutes / total_minutes * 100) if total_minutes > 0 else 0
                
                col1, col2 = st.columns([2, 3])
                with col1:
                    st.markdown(f"**{subject}**")
                with col2:
                    st.progress(percentage / 100)
                    st.caption(f"{hours:.1f}시간 ({minutes}분, {percentage:.0f}%)")
        
        st.divider()
        
        # ========================================
        # 집중도 분석
        # ========================================
        st.subheader("⭐ 집중도 분석")
        
        focus_scores = [s.get("payload", {}).get("focus", 0) for s in study_sessions if s.get("payload", {}).get("focus", 0) > 0]
        
        if focus_scores:
            avg_focus = sum(focus_scores) / len(focus_scores)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("평균 집중도", f"{avg_focus:.1f}/5.0")
                focus_stars = "⭐" * int(avg_focus)
                st.caption(focus_stars)
            with col2:
                # 집중도 분포
                focus_dist = {}
                for score in focus_scores:
                    focus_dist[score] = focus_dist.get(score, 0) + 1
                
                st.caption("집중도 분포:")
                for score in sorted(focus_dist.keys(), reverse=True):
                    count = focus_dist[score]
                    stars = "⭐" * score
                    st.caption(f"{stars}: {count}회")
        
        st.divider()
        
        # ========================================
        # 학습 주제 요약
        # ========================================
        st.subheader("📝 학습 주제 요약")
        
        all_topics = []
        for session in study_sessions:
            topics = session.get("payload", {}).get("topics", [])
            all_topics.extend(topics)
        
        if all_topics:
            # 주제별 빈도
            topic_counts = {}
            for topic in all_topics:
                topic_counts[topic] = topic_counts.get(topic, 0) + 1
            
            # 상위 5개 주제
            top_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            
            for topic, count in top_topics:
                st.caption(f"• {topic}: {count}회 학습")
        else:
            st.caption("기록된 학습 주제가 없습니다.")
        
        st.divider()
        
        # ========================================
        # 일별 학습 시간 추이
        # ========================================
        st.subheader("📈 일별 학습 시간")
        
        daily_times = {}
        for session in study_sessions:
            occurred_on = session.get("occurred_on", "")
            duration = session.get("payload", {}).get("duration_min", 0)
            daily_times[occurred_on] = daily_times.get(occurred_on, 0) + duration
        
        if daily_times:
            import pandas as pd
            
            # 날짜순 정렬
            sorted_dates = sorted(daily_times.keys())
            chart_data = {
                "날짜": sorted_dates,
                "학습 시간 (분)": [daily_times[d] for d in sorted_dates]
            }
            df = pd.DataFrame(chart_data)
            df["날짜"] = pd.to_datetime(df["날짜"])
            df = df.set_index("날짜")
            
            st.line_chart(df)
        
except Exception as e:
    st.error(f"❌ 리포트 생성 중 오류 발생: {e}")
