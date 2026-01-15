"""
ReflectOS - 개인 회고 & 시간 관리 MVP
메인 엔트리 포인트 (st.navigation 기반)
"""
import streamlit as st
from lib.auth import is_authenticated, get_current_user, logout
from lib.auth_ui import render_auth_page
from lib.modules import MODULE_REGISTRY, get_active_modules

# === 페이지 설정 (1회만 실행) ===
st.set_page_config(
    page_title="ReflectOS",
    page_icon="🪞",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === 인증 게이트 ===
if not is_authenticated():
    # 로그인 안 됨 → 인증 UI 렌더링
    render_auth_page()
    st.stop()

# === 로그인 후 처리 ===
user = get_current_user()
user_id = user.id

# 활성 모듈 로드
active_modules = get_active_modules(user_id)

# === 네비게이션 페이지 구성 ===
pages = []

# 공통 기능 그룹
pages.append(st.Page("pages/1_Home.py", title="Home", icon="🏠"))
pages.append(st.Page("pages/2_Checkin.py", title="Check-in", icon="✍️"))
pages.append(st.Page("pages/3_Report.py", title="Report", icon="📊"))
pages.append(st.Page("pages/4_Planner.py", title="Planner", icon="📅"))
pages.append(st.Page("pages/5_Memory.py", title="Memory", icon="🧠"))

# 모듈 그룹 (활성화된 것만 표시)
if "health" in active_modules:
    health_info = MODULE_REGISTRY["health"]
    pages.append(st.Page("pages/health/today.py", title="오늘 기록", icon="📝"))
    pages.append(st.Page("pages/health/weight.py", title="체중", icon="⚖️"))
    pages.append(st.Page("pages/health/exercise.py", title="운동", icon="🏋️"))
    pages.append(st.Page("pages/health/report.py", title="건강 리포트", icon="📈"))

# 설정 (항상 표시)
pages.append(st.Page("pages/6_Settings.py", title="Settings", icon="⚙️"))

# === 사이드바: 사용자 정보 + 로그아웃 ===
with st.sidebar:
    st.title("🪞 ReflectOS")
    st.caption("개인 회고 & 시간 관리")
    st.divider()
    
    if user:
        st.caption(f"👤 {user.email}")
    
    if st.button("🚪 로그아웃", key="logout_main"):
        logout()
        st.rerun()
    
    st.divider()

# === 네비게이션 실행 ===
pg = st.navigation(pages)
pg.run()
