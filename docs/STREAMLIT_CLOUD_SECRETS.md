# Streamlit Cloud Secrets 설정 가이드

## 📋 Secrets 설정 위치

Streamlit Cloud 앱 설정 페이지 → **"Secrets"** 탭

---

## 🔐 필수 Secrets

### Supabase 설정

```toml
[supabase]
url = "https://your-project-id.supabase.co"
key = "your-anon-public-key"
```

**설정 방법:**
1. Supabase 프로젝트 대시보드 접속
2. Settings > API 메뉴
3. Project URL 복사 → `url`에 입력
4. anon public key 복사 → `key`에 입력

---

### OpenAI 설정 (선택)

```toml
[openai]
api_key = "sk-..."
```

**설정 방법:**
1. [OpenAI Platform](https://platform.openai.com) 접속
2. API Keys 메뉴
3. 새 API 키 생성 또는 기존 키 복사

---

### Google OAuth 설정 (선택)

```toml
[google]
client_id = "your-client-id.apps.googleusercontent.com"
client_secret = "GOCSPX-..."
redirect_uri = "https://reflectos-main.streamlit.app/Settings"
```

**설정 방법:**
1. [Google Cloud Console](https://console.cloud.google.com) 접속
2. 프로젝트 선택 또는 생성
3. APIs & Services > Credentials
4. OAuth 2.0 Client ID 생성:
   - Application type: Web application
   - Authorized redirect URIs: `https://reflectos-main.streamlit.app/Settings`
5. Client ID와 Client Secret 복사

**중요:** `redirect_uri`는 Streamlit Cloud 배포 URL로 설정해야 합니다!

---

### 앱 설정

```toml
[app]
debug = false
default_timezone = "Asia/Seoul"
```

**설정:**
- `debug`: 개발 모드 (false 권장)
- `default_timezone`: 기본 시간대

---

## 📝 전체 Secrets 예시

```toml
# Supabase
[supabase]
url = "https://abcdefghijklmnop.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# OpenAI
[openai]
api_key = "sk-proj-abcdefghijklmnopqrstuvwxyz1234567890"

# Google OAuth
[google]
client_id = "123456789-abcdefghijklmnop.apps.googleusercontent.com"
client_secret = "GOCSPX-abcdefghijklmnopqrstuvwxyz"
redirect_uri = "https://reflectos-main.streamlit.app/Settings"

# 앱 설정
[app]
debug = false
default_timezone = "Asia/Seoul"
```

---

## ✅ 확인 방법

Secrets 저장 후:
1. 앱 재배포 (자동 또는 수동)
2. 앱 접속하여 로그인 테스트
3. 데이터 저장/조회 테스트

---

## 🔧 문제 해결

### Supabase 연결 오류
- URL과 key가 정확한지 확인
- Supabase 프로젝트의 Network 설정 확인

### Google OAuth 오류
- `redirect_uri`가 Streamlit Cloud URL과 정확히 일치하는지 확인
- Google Cloud Console에서 Redirect URI 등록 확인

### Secrets 저장 실패
- TOML 형식이 올바른지 확인
- 따옴표, 대괄호 등 문법 확인
