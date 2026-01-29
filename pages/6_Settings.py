"""
ReflectOS - Settings
연동 설정 및 환경 구성
Step 9: Google Calendar OAuth 연결
"""
import streamlit as st
import logging
from urllib.parse import parse_qs, urlparse
from lib.auth import get_current_user, is_authenticated

# 로깅 설정
logger = logging.getLogger(__name__)

# === 인증 체크 (치명 오류 방지) ===
if not is_authenticated():
    st.warning("⚠️ 로그인이 필요합니다.")
    st.info("로그인 페이지로 이동합니다...")
    st.stop()

# 사용자 정보 가져오기 (None 체크 강화 - 절대 user.id 직접 접근 금지)
user = get_current_user()
if user is None:
    logger.error("[SETTINGS] user is None - 로그인 필요")
    st.error("❌ 로그인이 필요합니다. 다시 로그인해주세요.")
    try:
        from lib.auth import logout
        logout()  # 세션 정리
    except:
        pass
    st.stop()

# user.id 안전하게 접근
user_id = getattr(user, "id", None)
if user_id is None:
    logger.error("[SETTINGS] user.id is None - 세션 만료")
    st.error("❌ 사용자 세션이 만료되었습니다. 다시 로그인해주세요.")
    try:
        from lib.auth import logout
        logout()  # 세션 정리
    except:
        pass
    st.stop()
user_email = getattr(user, 'email', 'unknown')
logger.info(f"[SETTINGS] 페이지 로드: user_id={user_id}, email={user_email}")

st.title("⚙️ Settings")
st.caption("연동 및 환경 설정을 관리하세요")


# === OAuth 콜백 처리 ===
# URL에 code 파라미터가 있으면 OAuth 콜백
# Streamlit 버전 호환성 처리
try:
    # Streamlit 1.30+
    query_params = dict(st.query_params)
except AttributeError:
    # Streamlit 이전 버전
    query_params = st.experimental_get_query_params()

if "code" in query_params:
    # query_params["code"]가 리스트일 수 있음
    auth_code = query_params["code"]
    if isinstance(auth_code, list):
        auth_code = auth_code[0]
    
    try:
        from lib.calendar_google import handle_oauth_callback
        
        with st.spinner("Google 계정 연결 중..."):
            if handle_oauth_callback(auth_code):
                st.success("✅ Google Calendar가 연결되었습니다!")
                # URL에서 code 파라미터 제거
                try:
                    st.query_params.clear()
                except AttributeError:
                    st.experimental_set_query_params()
                st.rerun()
            else:
                st.error("연결에 실패했습니다. 다시 시도해주세요.")
    except Exception as e:
        st.error(f"OAuth 처리 오류: {e}")


# === 연결 상태 ===
st.subheader("🔗 연결 상태")

col1, col2, col3 = st.columns(3)

with col1:
    with st.container():
        st.markdown("**🗄️ Supabase**")
        try:
            from lib.config import get_supabase_client
            client = get_supabase_client()
            if client:
                st.success("✅ 연결됨")
                
                # 간단한 연결 테스트
                try:
                    test = client.table("profiles").select("id").limit(1).execute()
                    st.caption("DB 접근 가능")
                except:
                    st.caption("⚠️ 테이블 접근 오류")
            else:
                st.error("❌ 연결 실패")
        except Exception as e:
            st.warning(f"⚠️ {e}")
            
with col2:
    with st.container():
        st.markdown("**🤖 OpenAI**")
        try:
            from lib.config import get_openai_api_key
            api_key = get_openai_api_key()
            if api_key:
                st.success("✅ API 키 설정됨")
                # 마스킹된 키 표시
                masked_key = api_key[:7] + "..." + api_key[-4:]
                st.caption(masked_key)
            else:
                st.error("❌ API 키 없음")
        except:
            st.warning("⚠️ 설정 필요")

with col3:
    with st.container():
        st.markdown("**📅 Google Calendar**")
        try:
            from lib.calendar_google import is_authenticated, logout
            
            if is_authenticated():
                st.success("✅ 연결됨")
                if st.button("🔓 연결 해제", key="google_logout"):
                    logout()
                    st.rerun()
            else:
                st.warning("⚠️ 연결 안됨")
        except ImportError:
            st.error("❌ 모듈 없음")
        except:
            st.warning("⚠️ 연결 안됨")


st.divider()

# === DB 상태 체크 ===
st.subheader("🗄️ DB 상태 확인")

try:
    from lib.config import get_supabase_client
    
    client = get_supabase_client()
    
    if client:
        if st.button("🔍 module_entries 테이블 확인", use_container_width=True):
            with st.spinner("테이블 존재 여부 확인 중..."):
                try:
                    # 테이블 조회로 확인 (간접적 방법)
                    try:
                        test_query = client.table("module_entries").select("id").limit(1).execute()
                        st.success("✅ module_entries 테이블이 존재하고 정상 작동 중입니다.")
                        st.caption("테이블이 schema cache에 등록되어 있습니다.")
                    except Exception as e:
                        error_str = str(e)
                        if "PGRST205" in error_str or "schema cache" in error_str.lower():
                            st.error("❌ 테이블이 schema cache에 없습니다.")
                            st.warning("""
                            **해결 방법:**
                            
                            1. Supabase SQL Editor에서 `sql/reload_pgrst_schema.sql` 실행
                            2. 앱을 새로고침하거나 재시작
                            """)
                        elif "permission" in error_str.lower() or "row-level security" in error_str.lower():
                            st.warning("⚠️ 테이블은 존재하지만 접근 권한이 없습니다.")
                            st.caption("RLS 정책을 확인하세요.")
                        else:
                            st.error(f"❌ 테이블 확인 실패: {error_str}")
                            
                except Exception as e:
                    st.error(f"❌ 확인 중 오류 발생: {e}")
                    st.info("""
                    **수동 확인 방법:**
                    
                    Supabase SQL Editor에서 다음을 실행하세요:
                    ```sql
                    SELECT to_regclass('public.module_entries') AS module_entries;
                    ```
                    
                    - 결과가 `public.module_entries`: 테이블 존재
                    - 결과가 `NULL`: 테이블 없음 → `sql/module_entries.sql` 실행 필요
                    """)
    else:
        st.warning("⚠️ Supabase 연결이 필요합니다.")
        
except Exception as e:
    st.error(f"DB 상태 확인 오류: {e}")


st.divider()

# === Google Calendar 연동 ===
st.subheader("📅 Google Calendar 연동")

try:
    from lib.calendar_google import is_authenticated, get_auth_url, get_today_events, sync_events_to_db
    from lib.config import get_google_credentials
    
    google_creds = get_google_credentials()
    
    if not google_creds:
        st.error("❌ Google OAuth 설정이 없습니다.")
        st.info("`.streamlit/secrets.toml`에 Google OAuth 정보를 설정해주세요.")
    else:
        with st.container():
            if is_authenticated():
                st.markdown("### ✅ Google Calendar 연결됨")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**오늘 일정 미리보기**")
                    
                    if st.button("🔄 일정 불러오기", key="fetch_today"):
                        with st.spinner("일정을 가져오는 중..."):
                            events = get_today_events()
                            
                            if events:
                                for event in events[:5]:  # 최대 5개
                                    start = event.get("start_time", "")
                                    if "T" in start:
                                        start_time = start.split("T")[1][:5]
                                    else:
                                        start_time = "종일"
                                    
                                    st.markdown(f"• `{start_time}` {event.get('title', '')}")
                            else:
                                st.info("오늘 일정이 없습니다.")
                
                with col2:
                    st.markdown("**데이터 동기화**")
                    
                    from datetime import datetime, timedelta
                    today = datetime.now().date()
                    week_start = today - timedelta(days=today.weekday())
                    week_end = week_start + timedelta(days=6)
                    
                    if st.button("📥 이번 주 일정 동기화", key="sync_week"):
                        with st.spinner("동기화 중..."):
                            count = sync_events_to_db(
                                week_start.isoformat(),
                                week_end.isoformat()
                            )
                            st.success(f"✅ {count}개 일정이 동기화되었습니다.")
                
                st.divider()
                
                if st.button("🔓 Google 연결 해제", use_container_width=True):
                    from lib.calendar_google import logout
                    logout()
                    st.success("연결이 해제되었습니다.")
                    st.rerun()
            
            else:
                st.markdown("### 🔗 Google Calendar 연결하기")
                st.markdown("""
                Google Calendar를 연결하면:
                - 📅 기존 일정을 플래너에서 확인
                - 🔄 일정을 자동으로 동기화
                - ✏️ 플래너에서 만든 계획을 캘린더에 추가 (Step 10)
                """)
                
                auth_url = get_auth_url()
                
                if auth_url:
                    st.link_button(
                        "🔑 Google 계정으로 연결",
                        auth_url,
                        use_container_width=True,
                        type="primary"
                    )
                    
                    st.caption("""
                    ℹ️ 버튼을 클릭하면 Google 로그인 페이지로 이동합니다.
                    로그인 후 권한을 허용하면 자동으로 돌아옵니다.
                    """)
                else:
                    st.error("인증 URL 생성 실패")

except ImportError as e:
    st.error(f"Google Calendar 모듈 로드 실패: {e}")
    st.info("필요한 패키지: google-api-python-client, google-auth-oauthlib")
except Exception as e:
    st.error(f"오류 발생: {e}")


st.divider()

# === 모듈 활성화 설정 ===
st.subheader("🔌 모듈 활성화")

try:
    from lib.modules import MODULE_REGISTRY, get_active_modules, set_active_modules
    from lib.config import get_supabase_client
    
    # 현재 활성 모듈 로드
    current_active = get_active_modules(user_id)
    
    logger.info(f"[SETTINGS] 현재 활성 모듈: user_id={user_id}, active={current_active}")
    
    st.caption("사용할 모듈을 선택하세요. 선택한 모듈이 메뉴에 표시됩니다.")
    
    # 모듈별 체크박스
    selected_modules = []
    for module_id, module_info in MODULE_REGISTRY.items():
        is_active = module_id in current_active
        checked = st.checkbox(
            f"{module_info['icon']} {module_info['name']}",
            value=is_active,
            help=module_info['description'],
            key=f"module_{module_id}"
        )
        if checked:
            selected_modules.append(module_id)
    
    logger.info(f"[SETTINGS] 선택된 모듈: user_id={user_id}, selected={selected_modules}")
    
    # 저장 버튼
    if st.button("💾 모듈 설정 저장", use_container_width=True, type="primary"):
        try:
            # 반환값 언패킹 (핵심 버그 수정)
            ok, msg = set_active_modules(user_id, selected_modules)
            
            if not ok:
                st.error(f"❌ 모듈 저장 실패: {msg}")
                logger.error(f"[SETTINGS] 저장 실패: user_id={user_id}, selected={selected_modules}, error={msg}")
                st.stop()  # 실패 시 여기서 중단
            
            # 저장 성공 시: 캐시 클리어 → 재조회 → rerun
            logger.info(f"[SETTINGS] 저장 성공: user_id={user_id}, saved_modules={selected_modules}, msg={msg}")
            
            # 캐시 클리어 (저장 직후 메뉴 갱신을 위해)
            get_active_modules.clear()
            
            # 즉시 재조회하여 실제 저장값 확인
            saved_active = get_active_modules(user_id)
            logger.info(f"[SETTINGS] 저장 후 재조회: user_id={user_id}, active_modules={saved_active}")
            
            # 성공 메시지
            st.success("✅ 모듈 설정이 저장되었습니다!")
            
            # 자동 갱신 (rerun)
            st.rerun()
            
        except Exception as e:
            error_msg = f"저장 중 오류 발생: {e}"
            logger.error(f"[SETTINGS] 저장 예외: user_id={user_id}, selected={selected_modules}, error={error_msg}")
            st.error(f"❌ {error_msg}")
    
except Exception as e:
    error_msg = f"모듈 설정 로드 오류: {e}"
    logger.error(f"[SETTINGS] 모듈 설정 로드 실패: {error_msg}")
    st.error(error_msg)


st.divider()

# === 프로필 설정 ===
st.subheader("👤 프로필")

try:
    from lib.config import get_supabase_client, get_current_user_id
    from lib.supabase_db import get_profile, upsert_profile
    
    client = get_supabase_client()
    user_id = get_current_user_id()
    
    # 기존 프로필 로드
    profile = get_profile(user_id) if client else None
    
    with st.form("profile_form"):
        display_name = st.text_input(
            "이름",
            value=profile.get("display_name", "User") if profile else "User"
        )
        
        timezone_options = ["Asia/Seoul", "Asia/Tokyo", "America/New_York", "Europe/London", "UTC"]
        current_tz = profile.get("timezone", "Asia/Seoul") if profile else "Asia/Seoul"
        timezone_idx = timezone_options.index(current_tz) if current_tz in timezone_options else 0
        
        timezone = st.selectbox(
            "시간대",
            options=timezone_options,
            index=timezone_idx
        )
        
        st.divider()
        
        st.markdown("**알림 설정** (향후 지원)")
        settings = profile.get("settings", {}) if profile else {}
        
        morning_reminder = st.toggle(
            "아침 체크인 알림 (09:00)",
            value=settings.get("morning_reminder", False),
            disabled=True
        )
        evening_reminder = st.toggle(
            "저녁 회고 알림 (21:00)",
            value=settings.get("evening_reminder", False),
            disabled=True
        )
        
        if st.form_submit_button("💾 저장", use_container_width=True):
            if client:
                result = upsert_profile({
                    "display_name": display_name,
                    "timezone": timezone,
                    "settings": {
                        **settings,
                        "morning_reminder": morning_reminder,
                        "evening_reminder": evening_reminder
                    }
                })
                
                if result:
                    st.success("✅ 프로필이 저장되었습니다!")
                else:
                    st.error("저장 실패")
            else:
                st.warning("Supabase 연결이 필요합니다.")

except Exception as e:
    st.error(f"프로필 로드 오류: {e}")


st.divider()

# === Secrets 설정 가이드 ===
st.subheader("🔐 Secrets 설정 가이드")

with st.expander("`.streamlit/secrets.toml` 설정 방법"):
    st.code("""
# .streamlit/secrets.toml

[supabase]
url = "https://your-project.supabase.co"
key = "your-anon-key"

[openai]
api_key = "sk-..."

[google]
client_id = "your-client-id.apps.googleusercontent.com"
client_secret = "GOCSPX-..."
redirect_uri = "http://localhost:8501/Settings"

[app]
debug = false
default_timezone = "Asia/Seoul"
    """, language="toml")
    
    st.markdown("""
    ### 설정 단계
    
    **1. Supabase**
    - [Supabase](https://supabase.com) 프로젝트 생성
    - Settings > API에서 URL과 anon key 복사
    
    **2. OpenAI**
    - [OpenAI Platform](https://platform.openai.com)에서 API 키 발급
    
    **3. Google Calendar**
    - [Google Cloud Console](https://console.cloud.google.com) 프로젝트 생성
    - APIs & Services > Credentials > OAuth 2.0 Client ID 생성
    - Redirect URI: `http://localhost:8501/Settings` (개발용)
    - 배포 시 실제 도메인으로 변경 필요
    """)


# === AI 자동화 ===
st.divider()
st.subheader("🤖 AI 자동화")
st.caption("체크인 저장 후 자동으로 RAG 인덱싱을 실행합니다. (Memory 동기화 버튼 없이 바로 검색 가능)")

try:
    from lib.supabase_db import get_profile, upsert_profile
    from lib.config import get_openai_api_key
    
    # 현재 프로필/설정 로드
    profile = get_profile()
    current_settings = (profile or {}).get("settings") or {}
    stored_value = bool(current_settings.get("auto_index_on_save", False))
    
    # 토글의 value는 세션에 우선권
    default_value = st.session_state.get("auto_index_on_save", stored_value)
    auto_index = st.toggle("✅ 체크인 저장 후 자동 인덱싱", value=default_value)
    st.session_state["auto_index_on_save"] = auto_index
    
    # 값이 바뀌었을 때만 저장
    if auto_index != stored_value:
        merged = dict(current_settings)
        merged["auto_index_on_save"] = auto_index
        upsert_profile({"settings": merged})
    
    # OpenAI 키 없을 때 안내
    if not get_openai_api_key():
        st.warning("OpenAI API 키가 없으면 자동 인덱싱이 동작하지 않습니다. (Settings 상단 OpenAI 상태를 확인하세요)")
        
except Exception as e:
    st.error(f"AI 자동화 설정 로드 오류: {e}")


# === 계정 관리 ===
st.divider()
st.subheader("🚪 계정 관리")

col1, col2 = st.columns(2)
with col1:
    st.info(f"로그인: {user.email}")
with col2:
    if st.button("🚪 로그아웃", type="primary", use_container_width=True):
        from lib.auth import logout
        logout()
        st.success("로그아웃되었습니다.")
        st.rerun()


# === 데이터 관리 ===
st.divider()
st.subheader("🗃️ 데이터 관리")

# --- 데모 데이터 섹션 (위험 구역 위에 배치) ---
st.markdown("#### 🎬 데모 데이터")
st.caption("테스트용 7일치 체크인 데이터를 생성합니다.")

demo_col1, demo_col2 = st.columns(2)

with demo_col1:
    demo_overwrite = st.checkbox(
        "기존 데모 데이터 삭제 후 재생성",
        value=True,
        key="demo_overwrite"
    )
    
    if st.button("📦 데모 데이터 7일 생성", use_container_width=True, type="primary"):
        try:
            from lib.demo_data import seed_demo_data
            
            with st.spinner("🔄 데모 데이터 생성 중... (임베딩 포함)"):
                result = seed_demo_data(
                    days=7,
                    overwrite=demo_overwrite,
                    also_index=True
                )
            
            if result.get("errors"):
                for err in result["errors"][:3]:  # 최대 3개만 표시
                    st.warning(f"⚠️ {err}")
            
            st.success(
                f"✅ 생성 완료!\n\n"
                f"- 삭제된 체크인: {result.get('deleted_demo_checkins', 0)}개\n"
                f"- 생성된 체크인: {result.get('inserted_checkins', 0)}개\n"
                f"- 생성된 추출: {result.get('inserted_extractions', 0)}개\n"
                f"- 인덱싱 완료: {result.get('indexed', 0)}개"
            )
            
        except Exception as e:
            st.error(f"오류 발생: {e}")

with demo_col2:
    st.caption("데모 태그(`__demo__`)가 있는 체크인만 삭제합니다.")
    
    # 삭제 안전장치
    confirm_demo_delete = st.text_input(
        "삭제 확인 문구",
        placeholder="DELETE DEMO",
        key="confirm_demo_delete"
    )
    can_delete_demo = (confirm_demo_delete.strip() == "DELETE DEMO")
    
    if st.button("🧹 데모 데이터만 삭제", use_container_width=True, disabled=not can_delete_demo):
        try:
            from lib.demo_data import delete_demo_data
            
            with st.spinner("🗑️ 데모 데이터 삭제 중..."):
                result = delete_demo_data()
            
            if result.get("errors"):
                for err in result["errors"][:3]:
                    st.warning(f"⚠️ {err}")
            
            st.success(
                f"✅ 삭제 완료!\n\n"
                f"- 삭제된 체크인: {result.get('deleted_checkins', 0)}개\n"
                f"- 삭제된 추출: {result.get('deleted_extractions', 0)}개\n"
                f"- 삭제된 임베딩: {result.get('deleted_embeddings', 0)}개"
            )
            
        except Exception as e:
            st.error(f"오류 발생: {e}")
    
    st.caption("⚠️ 삭제하려면 위 입력칸에 DELETE DEMO 를 정확히 입력하세요.")

st.divider()

with st.expander("⚠️ 위험 구역"):
    st.warning("아래 작업은 되돌릴 수 없습니다!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ 모든 체크인 삭제", type="secondary"):
            st.session_state.confirm_delete_checkins = True
        
        if st.session_state.get("confirm_delete_checkins"):
            st.error("정말 모든 체크인을 삭제하시겠습니까?")
            if st.button("✅ 예, 삭제합니다"):
                try:
                    client = get_supabase_client()
                    user_id = get_current_user_id()
                    if client:
                        client.table("checkins").delete().eq("user_id", user_id).execute()
                        st.success("삭제 완료")
                        st.session_state.confirm_delete_checkins = False
                except Exception as e:
                    st.error(f"삭제 실패: {e}")
    
    with col2:
        if st.button("🔄 벡터 인덱스 초기화", type="secondary"):
            st.session_state.confirm_reset_embeddings = True
        
        if st.session_state.get("confirm_reset_embeddings"):
            st.error("모든 임베딩을 삭제하시겠습니까?")
            if st.button("✅ 예, 초기화합니다"):
                try:
                    client = get_supabase_client()
                    user_id = get_current_user_id()
                    if client:
                        client.table("memory_embeddings").delete().eq("user_id", user_id).execute()
                        client.table("memory_chunks").delete().eq("user_id", user_id).execute()
                        st.success("초기화 완료")
                        st.session_state.confirm_reset_embeddings = False
                except Exception as e:
                    st.error(f"초기화 실패: {e}")
