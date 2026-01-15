"""
ReflectOS - 건강 모듈: 체중 그래프
최근 30일 체중 변화 차트
"""
import streamlit as st
from datetime import date, timedelta
import matplotlib.pyplot as plt
from lib.auth import get_current_user
from lib.supabase_db import get_module_entries
from lib.utils import setup_korean_font

# 사용자 정보 가져오기
user = get_current_user()
user_id = user.id

st.title("⚖️ 체중 변화")
st.caption("최근 30일 체중 추이를 확인하세요")

# 날짜 범위 설정
end_date = date.today()
start_date = end_date - timedelta(days=30)

# 체중 데이터 조회
try:
    entries = get_module_entries(
        user_id=user_id,
        module="health",
        entry_type="weight",
        date_range=(start_date, end_date),
        limit=100
    )
    
    if not entries:
        st.info("📭 아직 체중 기록이 없습니다. **오늘 기록** 페이지에서 첫 기록을 남겨보세요!")
    else:
        # 데이터 정렬 (날짜순)
        entries_sorted = sorted(entries, key=lambda x: x.get("occurred_on", ""))
        
        # 날짜와 체중 추출
        dates = []
        weights = []
        
        for entry in entries_sorted:
            occurred_on = entry.get("occurred_on")
            payload = entry.get("payload", {})
            weight = payload.get("weight")
            
            if occurred_on and weight:
                dates.append(occurred_on)
                weights.append(weight)
        
        if dates and weights:
            # 한글 폰트 설정
            setup_korean_font()
            
            # matplotlib 차트 생성
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(dates, weights, marker='o', linewidth=2, markersize=6)
            ax.set_xlabel("날짜")
            ax.set_ylabel("체중 (kg)")
            ax.set_title("체중 변화 추이")
            ax.grid(True, alpha=0.3)
            
            # x축 날짜 회전
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            st.pyplot(fig)
            
            # 통계 정보
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("최근 체중", f"{weights[-1]:.1f} kg")
            with col2:
                if len(weights) > 1:
                    change = weights[-1] - weights[0]
                    st.metric("30일 변화", f"{change:+.1f} kg", delta=f"{change:+.1f} kg")
                else:
                    st.metric("30일 변화", "-")
            with col3:
                if len(weights) > 1:
                    avg_weight = sum(weights) / len(weights)
                    st.metric("평균 체중", f"{avg_weight:.1f} kg")
                else:
                    st.metric("평균 체중", f"{weights[0]:.1f} kg")
        else:
            st.warning("체중 데이터가 없습니다.")
            
except Exception as e:
    st.error(f"❌ 데이터 조회 중 오류 발생: {e}")
