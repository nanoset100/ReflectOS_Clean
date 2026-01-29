"""
ReflectOS - 개인 회고 & 시간 관리 MVP
메인 엔트리 포인트 (st.navigation 기반)
"""
import streamlit as st
import logging
import os
from pathlib import Path
from lib.auth import is_authenticated, get_current_user, logout
from lib.modules import MODULE_REGISTRY, get_active_modules

# auth_ui import 오류 방지 (try-except)
try:
    from lib.auth_ui import render_auth_page
except (ImportError, KeyError) as e:
    logger = logging.getLogger(__name__)
    logger.error(f"[APP] lib.auth_ui import 실패: {e}")
    # fallback: auth_ui 없이도 작동하도록
    def render_auth_page():
        st.error("인증 모듈을 불러올 수 없습니다. 앱을 재시작해주세요.")
        st.stop()

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

# 활성 모듈 로드 (안전하게 처리)
try:
    active_modules = get_active_modules(user_id)
    # active_modules가 리스트가 아니면 빈 리스트로 초기화
    if not isinstance(active_modules, list):
        logger.warning(f"[APP] active_modules가 리스트가 아님: {type(active_modules)}, {active_modules}. 빈 리스트로 초기화.")
        active_modules = []
    # 레지스트리에 없는 모듈 제거
    active_modules = [m for m in active_modules if m in MODULE_REGISTRY]
    logger.info(f"[APP] 앱 초기화: user_id={user_id}, email={user_email}, active_modules={active_modules}")
except Exception as e:
    logger.error(f"[APP] 활성 모듈 로드 실패: {e}. 빈 리스트로 초기화.")
    active_modules = []

# === 네비게이션 페이지 구성 ===
pages = []

# 공통 기능 그룹 (고유한 url_pathname 지정)
pages.append(st.Page("pages/1_Home.py", title="Home", icon="🏠", url_pathname="home"))
pages.append(st.Page("pages/2_Checkin.py", title="Check-in", icon="✍️", url_pathname="checkin"))
pages.append(st.Page("pages/3_Report.py", title="Report", icon="📊", url_pathname="report"))
pages.append(st.Page("pages/4_Planner.py", title="Planner", icon="📅", url_pathname="planner"))
pages.append(st.Page("pages/5_Memory.py", title="Memory", icon="🧠", url_pathname="memory"))

# 모듈 그룹 (활성화된 것만 표시)
# Streamlit Cloud에서는 파일 존재 여부 체크가 부정확할 수 있으므로
# st.Page()에 직접 추가하고, Streamlit이 자체적으로 에러 처리하도록 함

if "health" in active_modules:
    health_info = MODULE_REGISTRY["health"]
    health_files = [
        ("pages/health/today.py", "오늘 기록", "📝", "health_today"),
        ("pages/health/weight.py", "체중", "⚖️", "health_weight"),
        ("pages/health/exercise.py", "운동", "🏋️", "health_exercise"),
        ("pages/health/report.py", "건강 리포트", "📈", "health_report")
    ]
    for file_path, title, icon, url_path in health_files:
        pages.append(st.Page(file_path, title=title, icon=icon, url_pathname=url_path))
    logger.info(f"[APP] 건강 모듈 페이지 등록: {len(health_files)}개")

if "student" in active_modules:
    student_info = MODULE_REGISTRY["student"]
    student_files = [
        ("pages/student/today.py", "오늘 학습", "📖", "student_today"),
        ("pages/student/subjects.py", "과목 목표", "📋", "student_subjects"),
        ("pages/student/report.py", "학습 리포트", "📊", "student_report"),
        ("pages/student/coaching.py", "슬럼프 로그", "😔", "student_coaching")
    ]
    for file_path, title, icon, url_path in student_files:
        pages.append(st.Page(file_path, title=title, icon=icon, url_pathname=url_path))
    logger.info(f"[APP] 수험생 모듈 페이지 등록: {len(student_files)}개 (active_modules={active_modules})")

if "jobseeker" in active_modules:
    jobseeker_info = MODULE_REGISTRY["jobseeker"]
    jobseeker_files = [
        ("pages/jobseeker/tracker.py", "지원 현황", "📮", "jobseeker_tracker"),
        ("pages/jobseeker/interview.py", "면접 기록", "💬", "jobseeker_interview"),
        ("pages/jobseeker/resume.py", "이력서 관리", "📄", "jobseeker_resume"),
        ("pages/jobseeker/report.py", "취준 리포트", "📊", "jobseeker_report")
    ]
    for file_path, title, icon, url_path in jobseeker_files:
        pages.append(st.Page(file_path, title=title, icon=icon, url_pathname=url_path))
    logger.info(f"[APP] 취준생 모듈 페이지 등록: {len(jobseeker_files)}개 (active_modules={active_modules})")

# 진단 로그: 환경 정보 (1회만 출력)
if not hasattr(st.session_state, "_env_logged"):
    logger.info(f"[APP] 작업 디렉토리: {os.getcwd()}")
    logger.info(f"[APP] app.py 위치: {__file__}")
    logger.info(f"[APP] 활성 모듈: {active_modules}")
    st.session_state._env_logged = True

# 설정 (항상 표시)
pages.append(st.Page("pages/6_Settings.py", title="Settings", icon="⚙️", url_pathname="settings"))

# === pages 리스트 검증 (st.navigation 오류 방지) ===
# None이나 잘못된 객체 제거
# isinstance(page, st.Page)는 Streamlit 버전에 따라 작동하지 않을 수 있으므로
# hasattr로 Page 객체인지 확인
valid_pages = []
for i, page in enumerate(pages):
    if page is None:
        logger.warning(f"[APP] pages[{i}]가 None입니다. 건너뜁니다.")
        continue
    # st.Page 객체인지 확인 (isinstance 대신 hasattr 사용)
    if not hasattr(page, '_script_path') and not hasattr(page, 'script_path'):
        logger.warning(f"[APP] pages[{i}]가 st.Page 객체가 아닙니다: {type(page)}. 건너뜁니다.")
        continue
    valid_pages.append(page)

logger.info(f"[APP] 페이지 구성 완료: 총 {len(valid_pages)}개 (원본 {len(pages)}개)")

# pages가 비어있으면 기본 페이지라도 추가
if not valid_pages:
    logger.error("[APP] 유효한 페이지가 없습니다! 기본 페이지를 추가합니다.")
    valid_pages.append(st.Page("pages/1_Home.py", title="Home", icon="🏠", url_pathname="home"))
    valid_pages.append(st.Page("pages/6_Settings.py", title="Settings", icon="⚙️", url_pathname="settings"))

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

# === 네비게이션 실행 (검증된 pages 사용) ===
try:
    pg = st.navigation(valid_pages)
    pg.run()
except Exception as e:
    logger.error(f"[APP] st.navigation 오류: {e}")
    logger.error(f"[APP] pages 리스트: {[str(p) for p in valid_pages]}")
    st.error(f"❌ 페이지 로드 오류가 발생했습니다: {e}")
    st.info("앱을 새로고침하거나 Settings에서 모듈 설정을 확인해주세요.")
    st.stop()
