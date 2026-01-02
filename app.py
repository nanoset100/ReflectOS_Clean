"""
ReflectOS - 개인 회고 & 시간 관리 MVP
메인 엔트리 포인트
"""
import streamlit as st

# === 페이지 설정 ===
st.set_page_config(
    page_title="ReflectOS",
    page_icon="🪞",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === 사이드바 브랜딩 ===
with st.sidebar:
    st.title("🪞 ReflectOS")
    st.caption("개인 회고 & 시간 관리")
    st.divider()

# === 메인 콘텐츠 (Home 리다이렉트) ===
st.title("🪞 ReflectOS에 오신 것을 환영합니다")
st.markdown("""
**ReflectOS**는 일상을 기록하고, AI와 함께 회고하며, 
시간을 효율적으로 관리하는 개인 생산성 도구입니다.

---

### 🚀 시작하기

왼쪽 사이드바에서 원하는 기능을 선택하세요:

| 페이지 | 설명 |
|--------|------|
| 🏠 **Home** | 대시보드 - 최근 기록 확인 |
| ✍️ **Check-in** | 오늘의 생각/감정 기록 |
| 📊 **Report** | 주간 회고 리포트 |
| 📅 **Planner** | 시간블록 일정 관리 |
| 🧠 **Memory** | RAG 기반 기억 검색 |
| ⚙️ **Settings** | 연동 및 설정 |

---

*💡 Tip: 매일 짧은 체크인으로 시작하세요!*
""")

# === 푸터 ===
st.divider()
st.caption("Made with ❤️ using Streamlit")

