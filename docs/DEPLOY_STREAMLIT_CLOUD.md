# ReflectOS Streamlit Cloud 배포 가이드

## 📋 사전 준비

### 1. GitHub 저장소 준비
- ReflectOS 코드가 GitHub 저장소에 푸시되어 있어야 합니다
- 또는 ZIP 파일로 업로드 가능

### 2. Streamlit Cloud 계정
- [Streamlit Cloud](https://streamlit.io/cloud)에 로그인
- GitHub 계정 연동 필요

---

## 🚀 Step 1: Streamlit Cloud 앱 생성

### 1-1. 새 앱 만들기
1. Streamlit Cloud 대시보드 접속
2. **"New app"** 또는 **"Create app"** 클릭

### 1-2. 저장소 연결
- **Repository**: ReflectOS GitHub 저장소 선택
- **Branch**: `main` 또는 배포할 브랜치 선택
- **Main file path**: `app.py` (프로젝트 루트 기준)

### 1-3. 앱 설정
- **App name**: `reflectos` (또는 원하는 이름)
- **URL**: 자동 생성됨 (예: `https://reflectos-main.streamlit.app`)

### 1-4. Secrets 설정
Streamlit Cloud Secrets에 다음 값들을 설정:

```toml
[supabase]
url = "https://your-project-id.supabase.co"
key = "your-anon-public-key"

[openai]
api_key = "sk-..."

[google]
client_id = "your-client-id.apps.googleusercontent.com"
client_secret = "your-client-secret"
redirect_uri = "https://reflectos-main.streamlit.app/Settings"

[app]
debug = false
default_timezone = "Asia/Seoul"
```

**설정 방법:**
1. 앱 설정 페이지에서 **"Secrets"** 탭 클릭
2. 위 TOML 형식으로 입력
3. **"Save"** 클릭

### 1-5. 배포
- **"Deploy"** 버튼 클릭
- 배포 완료까지 1-2분 소요

---

## ✅ Step 2: 배포 확인

### 2-1. 앱 접속
- 생성된 URL로 접속 (예: `https://reflectos-main.streamlit.app`)
- 정상 로드 확인

### 2-2. 기능 테스트
- [ ] 회원가입/로그인 정상 동작
- [ ] Supabase 연결 확인 (데이터 저장/조회)
- [ ] 모듈 활성화/비활성화 동작
- [ ] 기록 저장/조회 정상

### 2-3. URL 확정
- 배포 성공 후 최종 URL 확인
- 예: `https://reflectos-main.streamlit.app`
- 이 URL의 **hostname**을 기록해두세요 (TWA 설정에 필요)

---

## 🔧 문제 해결

### 배포 실패 시
1. **로그 확인**: Streamlit Cloud 앱 페이지에서 "Logs" 탭 확인
2. **의존성 확인**: `requirements.txt`에 모든 패키지 포함되어 있는지 확인
3. **Secrets 확인**: 모든 필수 secrets가 설정되어 있는지 확인

### Supabase 연결 오류
- Supabase URL과 key가 정확한지 확인
- Supabase 프로젝트의 Network 설정에서 Streamlit Cloud IP 허용 확인

### Google OAuth 오류
- `redirect_uri`가 Streamlit Cloud URL로 설정되어 있는지 확인
- Google Cloud Console에서 Redirect URI 등록 확인

---

## 📝 다음 단계

배포 완료 후:
1. **최종 URL 기록**: TWA Android 프로젝트 설정에 사용
2. **Bubblewrap TWA 프로젝트 생성**: `docs/DEPLOY_ANDROID_TWA.md` 참고

---

## 🔗 참고 링크

- [Streamlit Cloud 문서](https://docs.streamlit.io/streamlit-community-cloud)
- [Secrets 관리](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management)
