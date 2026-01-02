"""
ReflectOS - Google Calendar 연동
OAuth2 인증 및 일정 동기화
Step 9: 읽기 기능 구현
Step 10: 쓰기 기능 구현
"""
import streamlit as st
from typing import Optional, List, Dict
from datetime import datetime, timedelta
import json

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from lib.config import get_google_credentials, get_supabase_client, get_current_user_id


# === OAuth2 설정 ===
SCOPES = [
    'https://www.googleapis.com/auth/calendar.readonly',  # Step 9: 읽기
    'https://www.googleapis.com/auth/calendar.events',     # Step 10: 쓰기
]


def _get_flow() -> Optional[Flow]:
    """OAuth2 Flow 객체 생성"""
    creds = get_google_credentials()
    if not creds:
        return None
    
    client_config = {
        "web": {
            "client_id": creds["client_id"],
            "client_secret": creds["client_secret"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [creds["redirect_uri"]]
        }
    }
    
    flow = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=creds["redirect_uri"]
    )
    
    return flow


def _get_credentials_from_session() -> Optional[Credentials]:
    """세션에서 인증 정보 가져오기"""
    token_info = st.session_state.get("google_token")
    if not token_info:
        return None
    
    try:
        creds = Credentials(
            token=token_info.get("access_token"),
            refresh_token=token_info.get("refresh_token"),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=get_google_credentials()["client_id"],
            client_secret=get_google_credentials()["client_secret"],
            scopes=SCOPES
        )
        return creds
    except Exception as e:
        st.error(f"인증 정보 로드 실패: {e}")
        return None


def _save_token_to_db(token_info: Dict) -> bool:
    """토큰을 Supabase에 저장 (profiles 테이블의 settings 필드 활용)"""
    try:
        client = get_supabase_client()
        user_id = get_current_user_id()
        
        if not client:
            return False
        
        # profiles 테이블의 settings에 토큰 저장
        response = client.table("profiles").select("settings").eq("user_id", user_id).single().execute()
        
        current_settings = response.data.get("settings", {}) if response.data else {}
        current_settings["google_token"] = token_info
        
        client.table("profiles").update({
            "settings": current_settings
        }).eq("user_id", user_id).execute()
        
        return True
    except Exception as e:
        st.error(f"토큰 저장 실패: {e}")
        return False


def _load_token_from_db() -> Optional[Dict]:
    """Supabase에서 토큰 로드"""
    try:
        client = get_supabase_client()
        user_id = get_current_user_id()
        
        if not client:
            return None
        
        response = client.table("profiles").select("settings").eq("user_id", user_id).single().execute()
        
        if response.data:
            settings = response.data.get("settings", {})
            return settings.get("google_token")
        
        return None
    except:
        return None


# ============================================
# 인증 상태 확인
# ============================================

def is_authenticated() -> bool:
    """Google 인증 상태 확인"""
    # 세션에 토큰이 있는지 확인
    if st.session_state.get("google_authenticated"):
        return True
    
    # DB에서 토큰 로드 시도
    token = _load_token_from_db()
    if token:
        st.session_state.google_token = token
        st.session_state.google_authenticated = True
        return True
    
    return False


def get_auth_url() -> Optional[str]:
    """OAuth2 인증 URL 생성"""
    flow = _get_flow()
    if not flow:
        return None
    
    auth_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    
    # state 저장 (CSRF 방지)
    st.session_state.google_oauth_state = state
    
    return auth_url


def handle_oauth_callback(auth_code: str) -> bool:
    """
    OAuth2 콜백 처리
    
    Args:
        auth_code: Google에서 받은 authorization code
    
    Returns:
        성공 여부
    """
    try:
        flow = _get_flow()
        if not flow:
            return False
        
        # 토큰 교환
        flow.fetch_token(code=auth_code)
        credentials = flow.credentials
        
        # 토큰 정보 저장
        token_info = {
            "access_token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_uri": credentials.token_uri,
            "scopes": list(credentials.scopes),
            "expiry": credentials.expiry.isoformat() if credentials.expiry else None
        }
        
        # 세션에 저장
        st.session_state.google_token = token_info
        st.session_state.google_authenticated = True
        
        # DB에 저장
        _save_token_to_db(token_info)
        
        return True
        
    except Exception as e:
        st.error(f"OAuth 콜백 처리 실패: {e}")
        return False


def logout():
    """Google 로그아웃"""
    st.session_state.google_token = None
    st.session_state.google_authenticated = False
    
    # DB에서도 토큰 삭제
    try:
        client = get_supabase_client()
        user_id = get_current_user_id()
        
        if client:
            response = client.table("profiles").select("settings").eq("user_id", user_id).single().execute()
            if response.data:
                settings = response.data.get("settings", {})
                if "google_token" in settings:
                    del settings["google_token"]
                    client.table("profiles").update({"settings": settings}).eq("user_id", user_id).execute()
    except:
        pass


# ============================================
# Calendar API - 읽기 (Step 9)
# ============================================

def _get_calendar_service():
    """Google Calendar API 서비스 객체 생성"""
    creds = _get_credentials_from_session()
    if not creds:
        return None
    
    try:
        service = build('calendar', 'v3', credentials=creds)
        return service
    except Exception as e:
        st.error(f"Calendar 서비스 생성 실패: {e}")
        return None


def list_events(
    start_date: str,
    end_date: str,
    max_results: int = 50
) -> List[Dict]:
    """
    일정 목록 조회
    
    Args:
        start_date: 시작일 (YYYY-MM-DD)
        end_date: 종료일 (YYYY-MM-DD)
        max_results: 최대 결과 수
    
    Returns:
        일정 목록 [{title, start_time, end_time, description, ...}]
    """
    if not is_authenticated():
        return []
    
    service = _get_calendar_service()
    if not service:
        return []
    
    try:
        # 시간대 설정 (KST)
        time_min = f"{start_date}T00:00:00+09:00"
        time_max = f"{end_date}T23:59:59+09:00"
        
        events_result = service.events().list(
            calendarId='primary',
            timeMin=time_min,
            timeMax=time_max,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        # 형식 변환
        result = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            
            result.append({
                "external_id": event.get('id'),
                "title": event.get('summary', '(제목 없음)'),
                "description": event.get('description', ''),
                "start_time": start,
                "end_time": end,
                "location": event.get('location', ''),
                "attendees": [a.get('email') for a in event.get('attendees', [])],
                "provider": "google"
            })
        
        return result
        
    except HttpError as e:
        st.error(f"Calendar API 오류: {e}")
        return []
    except Exception as e:
        st.error(f"일정 조회 실패: {e}")
        return []


def sync_events_to_db(start_date: str, end_date: str) -> int:
    """
    Google Calendar 일정을 calendar_events 테이블에 동기화
    
    Args:
        start_date: 시작일
        end_date: 종료일
    
    Returns:
        동기화된 이벤트 수
    """
    events = list_events(start_date, end_date)
    if not events:
        return 0
    
    try:
        client = get_supabase_client()
        user_id = get_current_user_id()
        
        if not client:
            return 0
        
        synced_count = 0
        
        for event in events:
            # 기존 이벤트 확인 (external_id로)
            existing = client.table("calendar_events").select("id").eq("external_id", event["external_id"]).eq("user_id", user_id).execute()
            
            data = {
                "user_id": user_id,
                "external_id": event["external_id"],
                "provider": "google",
                "title": event["title"],
                "description": event.get("description", ""),
                "start_time": event["start_time"],
                "end_time": event["end_time"],
                "location": event.get("location", ""),
                "attendees": event.get("attendees", []),
                "synced_at": datetime.utcnow().isoformat()
            }
            
            if existing.data:
                # 업데이트
                client.table("calendar_events").update(data).eq("id", existing.data[0]["id"]).execute()
            else:
                # 삽입
                client.table("calendar_events").insert(data).execute()
            
            synced_count += 1
        
        return synced_count
        
    except Exception as e:
        st.error(f"동기화 실패: {e}")
        return 0


def get_today_events() -> List[Dict]:
    """오늘 일정 가져오기 (편의 함수)"""
    today = datetime.now().date().isoformat()
    return list_events(today, today)


def get_week_events() -> List[Dict]:
    """이번 주 일정 가져오기 (편의 함수)"""
    today = datetime.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    
    return list_events(start_of_week.isoformat(), end_of_week.isoformat())


# ============================================
# Calendar API - 쓰기 (Step 10)
# ============================================

def create_event(
    title: str,
    start_datetime: str,
    end_datetime: str,
    description: str = "",
    location: str = ""
) -> Optional[Dict]:
    """
    일정 생성
    
    Args:
        title: 일정 제목
        start_datetime: 시작 시간 (ISO format)
        end_datetime: 종료 시간 (ISO format)
        description: 상세 설명
        location: 장소
    
    Returns:
        생성된 일정 정보
    """
    if not is_authenticated():
        return None
    
    service = _get_calendar_service()
    if not service:
        return None
    
    try:
        event = {
            'summary': title,
            'description': description,
            'location': location,
            'start': {
                'dateTime': start_datetime,
                'timeZone': 'Asia/Seoul',
            },
            'end': {
                'dateTime': end_datetime,
                'timeZone': 'Asia/Seoul',
            },
        }
        
        created_event = service.events().insert(
            calendarId='primary',
            body=event
        ).execute()
        
        return {
            "external_id": created_event.get('id'),
            "title": created_event.get('summary'),
            "html_link": created_event.get('htmlLink')
        }
        
    except HttpError as e:
        st.error(f"일정 생성 실패: {e}")
        return None
    except Exception as e:
        st.error(f"오류 발생: {e}")
        return None


def create_events_from_plan(plan_date: str, blocks: List[Dict]) -> int:
    """
    시간블록들을 Google Calendar에 일괄 생성
    
    Args:
        plan_date: 날짜 (YYYY-MM-DD)
        blocks: 시간블록 목록 [{start_time, end_time, title, category}]
    
    Returns:
        생성된 이벤트 수
    """
    if not blocks:
        return 0
    
    created_count = 0
    
    for block in blocks:
        start_time = block.get("start_time", "09:00")
        end_time = block.get("end_time", "10:00")
        
        # ISO format으로 변환
        start_dt = f"{plan_date}T{start_time}:00+09:00"
        end_dt = f"{plan_date}T{end_time}:00+09:00"
        
        title = block.get("title", "")
        category = block.get("category", "")
        description = f"[ReflectOS] 카테고리: {category}"
        
        result = create_event(
            title=title,
            start_datetime=start_dt,
            end_datetime=end_dt,
            description=description
        )
        
        if result:
            created_count += 1
    
    return created_count
