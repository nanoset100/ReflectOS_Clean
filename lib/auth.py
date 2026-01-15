"""
ReflectOS - Supabase Auth 인증 모듈
로그인, 회원가입, 세션 관리 담당
"""
import streamlit as st
from lib.config import get_supabase_client
from lib.supabase_db import upsert_profile


def signup(email: str, password: str, display_name: str = None) -> tuple[bool, str]:
    """
    회원가입
    
    Args:
        email: 사용자 이메일
        password: 비밀번호 (6자 이상)
        display_name: 표시 이름 (선택, 없으면 이메일 앞부분)
    
    Returns:
        (성공여부, 메시지)
    
    처리 로직:
    1. Supabase Auth로 사용자 생성 (supabase.auth.sign_up)
    2. 성공 시 profiles 테이블에 프로필 레코드 생성
       - user_id: response.user.id
       - email: 입력받은 이메일
       - display_name: 입력값 또는 이메일@앞부분
       - timezone: "Asia/Seoul" (기본값)
    3. 예외 처리하여 (False, 에러메시지) 반환
    """
    try:
        supabase = get_supabase_client()
        if not supabase:
            return False, "Supabase 연결에 실패했습니다."
        
        # 비밀번호 길이 검증
        if len(password) < 6:
            return False, "비밀번호는 6자 이상이어야 합니다."
        
        # Supabase Auth로 사용자 생성
        response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        
        if not response.user:
            return False, "회원가입에 실패했습니다."
        
        user_id = response.user.id
        
        # display_name 설정 (없으면 이메일 앞부분 사용)
        if not display_name or not display_name.strip():
            display_name = email.split("@")[0]
        
        # profiles 테이블에 프로필 생성
        profile_data = {
            "display_name": display_name,
            "email": email,
            "timezone": "Asia/Seoul"
        }
        
        upsert_result = upsert_profile(profile_data, user_id=user_id)
        
        if upsert_result:
            return True, f"회원가입이 완료되었습니다! 이제 로그인해주세요."
        else:
            # Auth는 성공했지만 프로필 생성 실패한 경우
            return True, f"회원가입은 완료되었지만 프로필 생성에 실패했습니다. 로그인 후 설정에서 프로필을 완성해주세요."
            
    except Exception as e:
        # Supabase 에러 메시지 파싱
        error_msg = str(e)
        if "already registered" in error_msg.lower() or "already exists" in error_msg.lower():
            return False, "이미 등록된 이메일입니다."
        elif "invalid" in error_msg.lower() or "email" in error_msg.lower():
            return False, "유효하지 않은 이메일 형식입니다."
        else:
            return False, f"회원가입 중 오류가 발생했습니다: {error_msg}"


def login(email: str, password: str) -> tuple[bool, str]:
    """
    로그인
    
    Args:
        email: 사용자 이메일
        password: 비밀번호
    
    Returns:
        (성공여부, 메시지)
    
    처리 로직:
    1. Supabase Auth로 로그인 (supabase.auth.sign_in_with_password)
    2. 성공 시 세션에 사용자 정보 저장:
       - st.session_state["user"] = response.user
       - st.session_state["user_id"] = response.user.id
    3. 예외 처리하여 (False, 에러메시지) 반환
    """
    try:
        supabase = get_supabase_client()
        if not supabase:
            return False, "Supabase 연결에 실패했습니다."
        
        # Supabase Auth로 로그인
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        if not response.user:
            return False, "로그인에 실패했습니다."
        
        # 세션에 사용자 정보 및 세션 토큰 저장
        st.session_state["user"] = response.user
        st.session_state["user_id"] = response.user.id
        
        # Supabase 세션 저장 (RLS 작동을 위해 필수)
        if hasattr(response, 'session') and response.session:
            st.session_state["supabase_session"] = {
                "access_token": response.session.access_token,
                "refresh_token": response.session.refresh_token
            }
        
        return True, f"환영합니다, {response.user.email}님!"
        
    except Exception as e:
        error_msg = str(e)
        if "invalid" in error_msg.lower() and "password" in error_msg.lower():
            return False, "이메일 또는 비밀번호가 올바르지 않습니다."
        elif "email not confirmed" in error_msg.lower():
            return False, "이메일 인증이 필요합니다. (MVP에서는 이메일 인증을 비활성화해주세요)"
        else:
            return False, f"로그인 중 오류가 발생했습니다: {error_msg}"


def get_access_refresh_tokens() -> tuple[str, str] | None:
    """
    세션에서 access_token과 refresh_token을 안전하게 추출
    
    Returns:
        (access_token, refresh_token) 튜플 또는 None
    """
    if "supabase_session" not in st.session_state:
        return None
    
    session = st.session_state["supabase_session"]
    
    # 딕셔너리 형태인지 확인
    if isinstance(session, dict):
        access_token = session.get("access_token")
        refresh_token = session.get("refresh_token")
        
        if access_token and refresh_token:
            return (access_token, refresh_token)
    
    return None


def logout():
    """
    로그아웃
    
    처리 로직:
    1. Supabase Auth 로그아웃 (supabase.auth.sign_out)
    2. 세션 정리:
       - st.session_state에서 모든 인증 관련 키 삭제
    """
    try:
        supabase = get_supabase_client()
        if supabase:
            supabase.auth.sign_out()
    except Exception as e:
        # 로그아웃 실패해도 세션은 정리
        pass
    finally:
        # 세션 완전 정리 (모든 인증 관련 키)
        keys_to_remove = [
            "user",
            "user_id",
            "supabase_session",
            "is_authenticated"  # 혹시 남아있을 수 있는 임시 키
        ]
        for key in keys_to_remove:
            if key in st.session_state:
                del st.session_state[key]


def get_current_user():
    """
    현재 로그인된 사용자 정보 반환
    
    Returns:
        User 객체 or None
    """
    return st.session_state.get("user", None)


def is_authenticated() -> bool:
    """
    로그인 상태 확인
    
    Returns:
        로그인 여부 (True/False)
    """
    return "user" in st.session_state and st.session_state["user"] is not None


def require_auth():
    """
    페이지 접근 시 인증 필수 체크
    로그인 안 되어 있으면 인증 페이지로 강제 이동
    
    사용법:
        페이지 최상단에서 호출
        require_auth()  # 로그인 안 되면 여기서 멈춤
    """
    if not is_authenticated():
        st.warning("⚠️ 로그인이 필요합니다.")
        st.info("로그인 페이지로 이동합니다...")
        st.switch_page("pages/auth.py")
        st.stop()
