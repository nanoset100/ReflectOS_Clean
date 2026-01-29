"""
ReflectOS - 개인 회고 & 시간 관리 MVP
메인 엔트리 포인트 (st.navigation 기반)
"""
import streamlit as st
import logging
from pathlib import Path
from lib.auth import is_authenticated, get_current_user, logout
from lib.auth_ui import render_auth_page
from lib.modules import MODULE_REGISTRY, get_active_modules

# 로깅 설정
logger = logging.getLogger(__name__)

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

# === 로그인 후 처리 (치명 오류 방지) ===
user = get_current_user()
if user is None or getattr(user, "id", None) is None:
    st.error("❌ 사용자 정보를 불러올 수 없습니다. 다시 로그인해주세요.")
    try:
        logout()  # 세션 정리
    except:
        pass
    render_auth_page()  # 인증 화면으로 유도
    st.stop()

user_id = user.id
user_email = getattr(user, 'email', 'unknown')

# 활성 모듈 로드
active_modules = get_active_modules(user_id)
logger.info(f"[APP] 앱 초기화: user_id={user_id}, email={user_email}, active_modules={active_modules}")

# === 네비게이션 페이지 구성 ===
pages = []

# 공통 기능 그룹
pages.append(st.Page("pages/1_Home.py", title="Home", icon="🏠"))
pages.append(st.Page("pages/2_Checkin.py", title="Check-in", icon="✍️"))
pages.append(st.Page("pages/3_Report.py", title="Report", icon="📊"))
pages.append(st.Page("pages/4_Planner.py", title="Planner", icon="📅"))
pages.append(st.Page("pages/5_Memory.py", title="Memory", icon="🧠"))

# 모듈 그룹 (활성화된 것만 표시)
# 파일 존재 여부 확인 (Linux 대소문자 민감성 대응)

if "health" in active_modules:
    health_info = MODULE_REGISTRY["health"]
    health_files = [
        ("pages/health/today.py", "오늘 기록", "📝"),
        ("pages/health/weight.py", "체중", "⚖️"),
        ("pages/health/exercise.py", "운동", "🏋️"),
        ("pages/health/report.py", "건강 리포트", "📈")
    ]
    for file_path, title, icon in health_files:
        if Path(file_path).exists():
            pages.append(st.Page(file_path, title=title, icon=icon))
        else:
            logger.warning(f"[APP] 파일 없음 (건강 모듈): {file_path}")

if "student" in active_modules:
    student_info = MODULE_REGISTRY["student"]
    student_files = [
        ("pages/student/today.py", "오늘 학습", "📖"),
        ("pages/student/subjects.py", "과목 목표", "📋"),
        ("pages/student/report.py", "학습 리포트", "📊"),
        ("pages/student/coaching.py", "슬럼프 로그", "😔")
    ]
    missing_files = []
    for file_path, title, icon in student_files:
        if Path(file_path).exists():
            pages.append(st.Page(file_path, title=title, icon=icon))
        else:
            missing_files.append(file_path)
            logger.warning(f"[MISSING] 수험생 모듈 파일 없음: {file_path}")
    
    if missing_files:
        logger.error(f"[MISSING] 수험생 모듈 활성화됐지만 파일 누락: {missing_files}")

if "jobseeker" in active_modules:
    jobseeker_info = MODULE_REGISTRY["jobseeker"]
    jobseeker_files = [
        ("pages/jobseeker/tracker.py", "지원 현황", "📮"),
        ("pages/jobseeker/interview.py", "면접 기록", "💬"),
        ("pages/jobseeker/resume.py", "이력서 관리", "📄"),
        ("pages/jobseeker/report.py", "취준 리포트", "📊")
    ]
    missing_files = []
    for file_path, title, icon in jobseeker_files:
        if Path(file_path).exists():
            pages.append(st.Page(file_path, title=title, icon=icon))
        else:
            missing_files.append(file_path)
            logger.warning(f"[MISSING] 취준생 모듈 파일 없음: {file_path}")
    
    if missing_files:
        logger.error(f"[MISSING] 취준생 모듈 활성화됐지만 파일 누락: {missing_files}")

# 진단 로그: 파일 존재 여부 확인 (1회만 출력)
if not hasattr(st.session_state, "_file_check_logged"):
    logger.info("[APP] 파일 존재 여부 확인:")
    for module_id in ["health", "student", "jobseeker"]:
        if module_id == "health":
            files_to_check = [
                "pages/health/today.py", "pages/health/weight.py",
                "pages/health/exercise.py", "pages/health/report.py"
            ]
        elif module_id == "student":
            files_to_check = [
                "pages/student/today.py", "pages/student/subjects.py",
                "pages/student/report.py", "pages/student/coaching.py"
            ]
        else:  # jobseeker
            files_to_check = [
                "pages/jobseeker/tracker.py", "pages/jobseeker/interview.py",
                "pages/jobseeker/resume.py", "pages/jobseeker/report.py"
            ]
        
        for file_path in files_to_check:
            exists = Path(file_path).exists()
            logger.info(f"  {file_path}: {'✓' if exists else '✗'}")
    
    st.session_state._file_check_logged = True

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
