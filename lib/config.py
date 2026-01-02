"""
ReflectOS - 설정 관리
Streamlit secrets에서 설정값 로드
"""
import streamlit as st
from supabase import create_client, Client
from functools import lru_cache


def get_supabase_url() -> str:
    """Supabase URL 반환"""
    try:
        return st.secrets["supabase"]["url"]
    except KeyError:
        st.error("❌ Supabase URL이 설정되지 않았습니다. `.streamlit/secrets.toml`을 확인하세요.")
        return None


def get_supabase_key() -> str:
    """Supabase anon key 반환"""
    try:
        return st.secrets["supabase"]["key"]
    except KeyError:
        st.error("❌ Supabase Key가 설정되지 않았습니다.")
        return None


@st.cache_resource
def get_supabase_client() -> Client:
    """
    Supabase 클라이언트 싱글톤 반환
    @st.cache_resource로 앱 전체에서 재사용
    """
    url = get_supabase_url()
    key = get_supabase_key()
    
    if not url or not key:
        return None
    
    try:
        client = create_client(url, key)
        return client
    except Exception as e:
        st.error(f"❌ Supabase 연결 실패: {e}")
        return None


def get_openai_api_key() -> str:
    """OpenAI API 키 반환"""
    try:
        return st.secrets["openai"]["api_key"]
    except KeyError:
        return None


def get_google_credentials() -> dict:
    """Google OAuth 설정 반환"""
    try:
        return {
            "client_id": st.secrets["google"]["client_id"],
            "client_secret": st.secrets["google"]["client_secret"],
            "redirect_uri": st.secrets["google"].get("redirect_uri", "http://localhost:8501")
        }
    except KeyError:
        return None


def get_app_config() -> dict:
    """앱 설정 반환"""
    try:
        return {
            "debug": st.secrets["app"].get("debug", False),
            "timezone": st.secrets["app"].get("default_timezone", "Asia/Seoul")
        }
    except KeyError:
        return {
            "debug": False,
            "timezone": "Asia/Seoul"
        }


# === 현재 사용자 ID (MVP: 단일 사용자) ===
def get_current_user_id() -> str:
    """
    현재 사용자 ID 반환
    MVP에서는 고정 ID 사용, 추후 인증 연동시 수정
    """
    # TODO: 실제 인증 구현 시 session_state에서 가져오기
    return "default-user-id"

