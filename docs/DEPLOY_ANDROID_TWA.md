# ReflectOS Android TWA 배포 가이드

## 📋 사전 준비

### 1. Streamlit Cloud URL 확정
- Step 1에서 배포한 Streamlit Cloud URL 확인
- 예: `https://reflectos-main.streamlit.app`
- **hostname**: `reflectos-main.streamlit.app` (프로토콜 제외)

### 2. Node.js 설치
- [Node.js](https://nodejs.org/) 16.x 이상 설치 필요
- Bubblewrap CLI 사용을 위해

### 3. Java JDK 설치
- Android 빌드를 위해 JDK 11 이상 필요

---

## 🚀 Step 2: Bubblewrap TWA 프로젝트 생성

### 2-1. 방법 A: FaithLoop-Android 복사 (권장)

**FaithLoop.zip 파일이 있는 경우:**

```bash
# FaithLoop.zip 압축 해제
unzip FaithLoop.zip

# FaithLoop-Android 폴더 복사
cp -r FaithLoop_extracted/FaithLoop-Android ReflectOS-Android
cd ReflectOS-Android
```

**Windows PowerShell:**
```powershell
# FaithLoop.zip 압축 해제
Expand-Archive -Path "FaithLoop.zip" -DestinationPath "FaithLoop_extracted" -Force

# FaithLoop-Android 폴더 복사
Copy-Item -Path "FaithLoop_extracted\FaithLoop-Android" -Destination "ReflectOS-Android" -Recurse
cd ReflectOS-Android
```

**상세 설정 가이드:** [REFLECTOS_ANDROID_SETUP.md](./REFLECTOS_ANDROID_SETUP.md) 참고

### 2-2. 방법 B: Bubblewrap으로 신규 생성

```bash
# Bubblewrap CLI 설치
npm install -g @bubblewrap/cli

# 새 프로젝트 생성
bubblewrap init --manifest https://reflectos-main.streamlit.app/manifest.json
```

**또는 수동 생성:**
```bash
mkdir ReflectOS-Android
cd ReflectOS-Android
bubblewrap init
```

---

## ⚙️ Step 3: 프로젝트 설정 수정

**상세 가이드:** [REFLECTOS_ANDROID_SETUP.md](./REFLECTOS_ANDROID_SETUP.md) 참고

### 3-1. `app/build.gradle` 수정

**FaithLoop-Android 기반으로 변경할 값들:**

```gradle
def twaManifest = [
    applicationId: 'com.reflectos.app',  // 변경: com.faithloop.app → com.reflectos.app
    hostName: 'reflectos-xxxx.streamlit.app',  // 변경: Streamlit Cloud URL의 hostname
    name: 'ReflectOS',  // 변경: FaithLoop → ReflectOS
    launcherName: 'ReflectOS',  // 변경
    themeColor: '#FF6B6B',  // 변경: 원하는 색상
    // ... 기타 설정
]

android {
    namespace "com.reflectos.app"  // 변경
    defaultConfig {
        applicationId "com.reflectos.app"  // 변경
        versionCode 1  // 첫 업로드면 1
        versionName "1.0.0"
        // ... 기타 설정
    }
    signingConfigs {
        release {
            keyAlias "reflectos"  // 변경: faithloop → reflectos
            // ... 기타 설정
        }
    }
}
```

**전체 예시 파일:** [android/app/build.gradle.example](../android/app/build.gradle.example) 참고

### 3-2. `app/src/main/AndroidManifest.xml` 수정

**package 속성 변경:**

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.reflectos.app">  <!-- 변경: com.faithloop.app → com.reflectos.app -->
```

**참고:** AGP 8.x에서는 `namespace`가 `build.gradle`에서 관리되지만, `package` 속성은 경로 참조용으로 필요합니다.

**전체 예시 파일:** [android/app/src/main/AndroidManifest.xml.example](../android/app/src/main/AndroidManifest.xml.example) 참고

### 3-3. `twa-manifest.json` 수정

**프로젝트 루트의 `twa-manifest.json` 수정:**

```json
{
  "packageId": "com.reflectos.app",  // 변경
  "host": "reflectos-xxxx.streamlit.app",  // 변경
  "name": "ReflectOS",  // 변경
  "launcherName": "ReflectOS",  // 변경
  "appVersionCode": 1,  // 변경: 첫 업로드면 1
  "appVersionName": "1.0.0",  // 변경
  "signingKey": {
    "alias": "reflectos"  // 변경: faithloop → reflectos
  }
  // ... 기타 설정
}
```

**전체 예시 파일:** [android/twa-manifest.json.example](../android/twa-manifest.json.example) 참고

### 3-4. 아이콘/스플래시 리소스 교체

**필요한 아이콘:**
- `app/src/main/res/mipmap-xxxhdpi/ic_launcher.png` (192x192)
- `app/src/main/res/mipmap-xxxhdpi/ic_launcher_round.png` (512x512)
- `app/src/main/res/drawable/ic_notification_icon.png` (알림 아이콘)
- `app/src/main/res/drawable/splash.xml` (스플래시 화면)

**ReflectOS 아이콘으로 교체:**
- 기존 FaithLoop 아이콘 삭제
- ReflectOS 아이콘 파일로 교체

---

## 🔐 Step 4: 서명 키 설정

### 4-1. 기존 keystore 재사용 (권장)

FaithLoop에서 사용한 keystore를 그대로 사용 가능:

```bash
# keystore 파일 위치 확인
# app/keystore.jks (또는 다른 위치)
```

### 4-2. 새 keystore 생성 (선택)

```bash
keytool -genkey -v -keystore reflectos-release-key.jks \
  -keyalg RSA -keysize 2048 -validity 10000 \
  -alias reflectos-key
```

**정보 입력:**
- 이름, 조직 등 입력
- 비밀번호 기록 (나중에 필요)

---

## 📦 Step 5: AAB 빌드

### 5-1. 환경변수 설정 (Windows PowerShell)

```powershell
$env:KEYSTORE_PASSWORD='your-keystore-password'
$env:KEY_ALIAS='reflectos-key'  # 또는 기존 alias
$env:KEY_PASSWORD='your-key-password'
```

### 5-2. 빌드 실행

```bash
# Windows
.\gradlew.bat clean bundleRelease

# macOS/Linux
./gradlew clean bundleRelease
```

### 5-3. 빌드 결과 확인

**AAB 파일 위치:**
```
app/build/outputs/bundle/release/app-release.aab
```

**확인 사항:**
- 파일 크기: 보통 5-15MB
- 생성 시간: 최근 시간인지 확인

---

## 📤 Step 6: Google Play Console 업로드

### 6-1. 새 앱 생성

1. [Google Play Console](https://play.google.com/console) 접속
2. **"앱 만들기"** 클릭
3. **"새 앱"** 선택

### 6-2. 앱 정보 입력

- **앱 이름**: ReflectOS
- **기본 언어**: 한국어
- **앱 또는 게임**: 앱
- **무료 또는 유료**: 무료
- **동의 및 계속** 클릭

### 6-3. 테스트 트랙 선택

**권장: 비공개 테스트 (Closed testing)**
- FaithLoop에서 내부 테스트 → 비공개 전환 시 versionCode 충돌 경험
- ReflectOS는 처음부터 **비공개 테스트**로 시작 권장

**선택:**
- 비공개 테스트 (Closed testing) ← 권장
- 내부 테스트 (Internal testing)

### 6-4. AAB 업로드

1. 선택한 테스트 트랙에서 **"새 버전 만들기"** 클릭
2. **"앱 번들 업로드"** 클릭
3. `app-release.aab` 파일 선택
4. 업로드 완료 대기

### 6-5. 업로드 오류 처리

**"버전코드 이미 사용됨" 오류:**
- `app/build.gradle`에서 `versionCode`를 +1 증가
- 재빌드 후 다시 업로드

**예:**
```gradle
versionCode = 2  // 1에서 2로 증가
```

### 6-6. 스토어 정보 입력 (선택)

- 앱 설명
- 스크린샷
- 아이콘
- 개인정보처리방침 URL

**참고:** 테스트 트랙에서는 최소 정보만 입력해도 업로드 가능

---

## ✅ Step 7: 최종 확인

### 7-1. 패키지명 확인
- **ReflectOS**: `com.reflectos.app`
- **FaithLoop**: `com.faithloop.app`
- ✅ 서로 다름 확인

### 7-2. 호스트명 확인
- **ReflectOS**: `reflectos-main.streamlit.app`
- **FaithLoop**: `faithloop.streamlit.app`
- ✅ 서로 다름 확인

### 7-3. Play Console 앱 확인
- **ReflectOS**: 새로 생성된 앱
- **FaithLoop**: 기존 앱
- ✅ 서로 다른 앱 확인

### 7-4. 버전코드 확인
- ReflectOS 첫 업로드: `versionCode = 1` ✅
- 같은 앱 내에서만 증가 규칙 적용 ✅

---

## 🔧 문제 해결

### 빌드 실패
- JDK 버전 확인 (11 이상)
- Gradle 버전 확인
- `gradlew` 실행 권한 확인 (Linux/Mac)

### 업로드 실패
- AAB 파일 크기 확인 (100MB 이하)
- 서명 확인
- Play Console 권한 확인

### 앱 실행 오류
- Streamlit Cloud URL 접근 가능한지 확인
- 네트워크 권한 확인
- TWA 설정 확인

---

## 📝 체크리스트

- [ ] Streamlit Cloud 배포 완료
- [ ] 최종 URL 확정 및 기록
- [ ] Bubblewrap 프로젝트 생성
- [ ] `build.gradle` 수정 (applicationId, hostName, versionCode)
- [ ] `AndroidManifest.xml` package 속성 제거
- [ ] 아이콘/스플래시 리소스 교체
- [ ] AAB 빌드 성공
- [ ] Play Console 새 앱 생성
- [ ] AAB 업로드 성공
- [ ] 테스트 설치 및 실행 확인

---

## 🔗 참고 링크

- [Bubblewrap 문서](https://github.com/GoogleChromeLabs/bubblewrap)
- [TWA 가이드](https://developer.chrome.com/docs/android/trusted-web-activity/)
- [Play Console 가이드](https://support.google.com/googleplay/android-developer)
