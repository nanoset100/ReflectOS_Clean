# ReflectOS 배포 체크리스트

## 📋 전체 배포 프로세스 요약

1. **Streamlit Cloud 배포** → ReflectOS 웹 앱 배포
2. **Bubblewrap TWA 생성** → Android 앱 프로젝트 생성
3. **AAB 빌드** → Android 앱 번들 생성
4. **Play Console 업로드** → Google Play에 새 앱 등록

---

## ✅ Step 1: Streamlit Cloud 배포

### 사전 준비
- [ ] GitHub 저장소에 ReflectOS 코드 푸시 완료
- [ ] Streamlit Cloud 계정 생성 및 GitHub 연동

### 앱 생성
- [ ] Streamlit Cloud에서 "New app" 클릭
- [ ] Repository: ReflectOS 저장소 선택
- [ ] Branch: `main` 선택
- [ ] Main file path: `app.py` 입력
- [ ] App name: `reflectos` 입력

### Secrets 설정
- [ ] Supabase URL 설정
- [ ] Supabase anon key 설정
- [ ] OpenAI API key 설정 (필요시)
- [ ] Google OAuth 설정 (필요시)
- [ ] redirect_uri를 Streamlit Cloud URL로 변경

### 배포 확인
- [ ] 배포 성공 확인
- [ ] 앱 URL 접속 테스트
- [ ] 로그인/회원가입 테스트
- [ ] 데이터 저장/조회 테스트
- [ ] **최종 URL 기록**: `https://reflectos-xxxx.streamlit.app`
- [ ] **hostname 기록**: `reflectos-xxxx.streamlit.app`

---

## ✅ Step 2: Bubblewrap TWA 프로젝트 생성

### 프로젝트 생성
- [ ] 방법 선택:
  - [ ] A: FaithLoop-Android 복사 후 수정
  - [ ] B: Bubblewrap CLI로 신규 생성

### 프로젝트 설정
- [ ] `app/build.gradle` 수정:
  - [ ] `namespace = "com.reflectos.app"`
  - [ ] `applicationId = "com.reflectos.app"`
  - [ ] `versionCode = 1` (첫 업로드)
  - [ ] `versionName = "1.0.0"`
  - [ ] `twaManifest.applicationId = "com.reflectos.app"`
  - [ ] `twaManifest.hostName = "reflectos-xxxx.streamlit.app"` (Step 1에서 기록한 값)
  - [ ] `twaManifest.name = "ReflectOS"`
  - [ ] `twaManifest.launcherName = "ReflectOS"`

- [ ] `app/src/main/AndroidManifest.xml` 수정:
  - [ ] `package="..."` 속성 제거

- [ ] 아이콘/리소스 교체:
  - [ ] ReflectOS 아이콘으로 교체 (192x192, 512x512)
  - [ ] 스플래시 화면 교체

---

## ✅ Step 3: 서명 및 빌드

### 서명 설정
- [ ] 방법 선택:
  - [ ] A: 기존 keystore 재사용
  - [ ] B: 새 keystore 생성

- [ ] keystore 정보 기록:
  - [ ] keystore 파일 경로
  - [ ] keystore 비밀번호
  - [ ] key alias
  - [ ] key 비밀번호

### 빌드
- [ ] 환경변수 설정 (Windows PowerShell):
  ```powershell
  $env:KEYSTORE_PASSWORD='...'
  $env:KEY_ALIAS='...'
  $env:KEY_PASSWORD='...'
  ```

- [ ] 빌드 실행:
  ```bash
  .\gradlew.bat clean bundleRelease
  ```

- [ ] 빌드 결과 확인:
  - [ ] `app/build/outputs/bundle/release/app-release.aab` 파일 생성 확인
  - [ ] 파일 크기 확인 (5-15MB 정도)

---

## ✅ Step 4: Google Play Console 업로드

### 새 앱 생성
- [ ] Play Console 접속
- [ ] "앱 만들기" 클릭
- [ ] 앱 정보 입력:
  - [ ] 앱 이름: ReflectOS
  - [ ] 기본 언어: 한국어
  - [ ] 앱 또는 게임: 앱
  - [ ] 무료 또는 유료: 무료

### 테스트 트랙 선택
- [ ] **비공개 테스트 (Closed testing)** 선택 ← 권장
- [ ] 또는 내부 테스트 선택

### AAB 업로드
- [ ] "새 버전 만들기" 클릭
- [ ] "앱 번들 업로드" 클릭
- [ ] `app-release.aab` 파일 선택
- [ ] 업로드 완료 대기

### 오류 처리
- [ ] "버전코드 이미 사용됨" 오류 발생 시:
  - [ ] `build.gradle`에서 `versionCode` +1 증가
  - [ ] 재빌드 후 다시 업로드

---

## ✅ Step 5: 최종 확인

### 독립성 확인
- [ ] **패키지명**:
  - [ ] ReflectOS: `com.reflectos.app`
  - [ ] FaithLoop: `com.faithloop.app`
  - [ ] ✅ 서로 다름 확인

- [ ] **호스트명**:
  - [ ] ReflectOS: `reflectos-xxxx.streamlit.app`
  - [ ] FaithLoop: `faithloop.streamlit.app`
  - [ ] ✅ 서로 다름 확인

- [ ] **Play Console 앱**:
  - [ ] ReflectOS: 새로 생성된 앱
  - [ ] FaithLoop: 기존 앱
  - [ ] ✅ 서로 다른 앱 확인

- [ ] **버전코드**:
  - [ ] ReflectOS 첫 업로드: `versionCode = 1` ✅
  - [ ] 같은 앱 내에서만 증가 규칙 적용 ✅

### 기능 테스트
- [ ] 앱 설치 확인
- [ ] 앱 실행 확인
- [ ] Streamlit Cloud URL 로드 확인
- [ ] 로그인/기능 동작 확인

---

## 📝 중요 정보 기록

### Streamlit Cloud
- **URL**: `https://reflectos-xxxx.streamlit.app`
- **hostname**: `reflectos-xxxx.streamlit.app`

### Android TWA
- **packageName**: `com.reflectos.app`
- **versionCode**: `1` (첫 업로드)
- **versionName**: `1.0.0`

### Play Console
- **앱 이름**: ReflectOS
- **테스트 트랙**: 비공개 테스트 (Closed testing)

---

## 🔗 관련 문서

- [Streamlit Cloud 배포 가이드](./DEPLOY_STREAMLIT_CLOUD.md)
- [Android TWA 배포 가이드](./DEPLOY_ANDROID_TWA.md)
