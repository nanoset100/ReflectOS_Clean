"""
🔐 ReflectOS 인증 페이지
로그인과 회원가입을 2컬럼으로 나란히 배치
(참고: 이 파일은 lib/auth_ui.py로 대체되었지만, 직접 접근 시를 위해 유지)
"""
import streamlit as st
import time
from lib.auth import login, signup

# 스타일: 중앙 정렬 + 카드 스타일
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    .stButton > button {
        width: 100%;
    }
    /* 폼 카드 스타일 */
    .element-container {
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# 헤더: 중앙 정렬
st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
st.markdown("### 🪞 ReflectOS")
st.caption("AI+RAG 신앙일기로 경단·기도·적용을 누적하고, 근거 기반으로 너를 돌아보며 작은 실천을 지속합니다.")
st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# 메인 레이아웃: 2컬럼 (로그인 / 회원가입)
col1, col2 = st.columns(2, gap="large")

# ========================================
# 왼쪽 컬럼: 로그인
# ========================================
with col1:
    st.subheader("🔐 로그인")
    
    with st.form("login_form", clear_on_submit=False):
        login_email = st.text_input(
            "이메일",
            placeholder="example@email.com",
            key="login_email"
        )
        
        login_password = st.text_input(
            "비밀번호",
            type="password",
            key="login_password"
        )
        
        login_submit = st.form_submit_button(
            "로그인",
            type="primary",
            use_container_width=True
        )
        
        if login_submit:
            # 유효성 검사
            if not login_email or not login_password:
                st.error("❌ 이메일과 비밀번호를 입력해주세요.")
            else:
                # 로그인 시도
                with st.spinner("로그인 중..."):
                    success, message = login(login_email, login_password)
                
                if success:
                    st.success(f"✅ {message}")
                    time.sleep(0.5)
                    st.switch_page("app.py")  # 메인 페이지로 이동
                else:
                    st.error(f"❌ {message}")

# ========================================
# 오른쪽 컬럼: 회원가입
# ========================================
with col2:
    st.subheader("📝 회원가입")
    
    with st.form("signup_form", clear_on_submit=False):
        signup_email = st.text_input(
            "이메일",
            placeholder="example@email.com",
            key="signup_email"
        )
        
        signup_password = st.text_input(
            "비밀번호 (6자 이상)",
            type="password",
            key="signup_password"
        )
        
        signup_password_confirm = st.text_input(
            "비밀번호 확인",
            type="password",
            key="signup_password_confirm"
        )
        
        signup_name = st.text_input(
            "이름 (선택)",
            placeholder="홍길동",
            key="signup_name"
        )
        
        signup_submit = st.form_submit_button(
            "회원가입",
            type="primary",
            use_container_width=True
        )
        
        if signup_submit:
            # 유효성 검사
            if not signup_email or not signup_password:
                st.error("❌ 이메일과 비밀번호는 필수입니다.")
            elif len(signup_password) < 6:
                st.error("❌ 비밀번호는 6자 이상이어야 합니다.")
            elif signup_password != signup_password_confirm:
                st.error("❌ 비밀번호가 일치하지 않습니다.")
            else:
                # 회원가입 시도
                with st.spinner("회원가입 중..."):
                    success, message = signup(signup_email, signup_password, signup_name)
                
                if success:
                    st.success(f"✅ {message}")
                    st.balloons()
                    st.info("🔐 이제 왼쪽에서 로그인해주세요!")
                else:
                    st.error(f"❌ {message}")

# 하단 안내 메시지
st.divider()
st.markdown("""
<div style='text-align: center; color: #666;'>
처음 오셨나요? 오른쪽에서 회원가입 후, 왼쪽에서 로그인하세요.
</div>
""", unsafe_allow_html=True)

# 하단 여백
st.markdown("<br>", unsafe_allow_html=True)
