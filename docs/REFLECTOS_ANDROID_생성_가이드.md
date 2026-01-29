# ReflectOS-Android 프로젝트 생성 가이드

## 📋 FaithLoop ↔ ReflectOS 관계

**FaithLoop:**
- 이미 Play Console에 "FaithLoop"로 등록됨 (비공개/테스트 진행 중)
- Android 패키지/서명키/버전코드가 이미 존재함
- packageName: `com.faithloop.app`
- hostName: `faithloop.streamlit.app`

**ReflectOS:**
- FaithLoop에서 파생된 코드지만 Play Console에서는 완전 별개의 새 앱으로 등록해야 함
- 새 packageName: `com.reflectos.app`
- 새 Streamlit URL: `https://reflectos.streamlit.app`
- 새 Android 프로젝트: `ReflectOS-Android`

**핵심 원칙:** "서로의 appId/packageName/hostName/versionCode/release track" 절대 섞지 않기

---

## 🚀 단계별 작업 지시

### Step A. Streamlit Cloud(웹) 쪽 확정 체크

#### A-1. ReflectOS URL 확정
- ✅ **확정 URL**: `https://reflectos.streamlit.app` (정상 접속 OK)

#### A-2. Streamlit Cloud 로그 확인
- Streamlit Cloud 대시보드 → 앱 선택 → **"Manage app"** → **"Logs"** 클릭
- 추가 `ModuleNotFoundError`가 없는지 확인
- matplotlib 설치 확인:
  ```
  Collecting matplotlib>=3.7,<4
  Successfully installed matplotlib-3.x.x
  ```

#### A-3. requirements.txt 확인
- ✅ **현재 상태**: `matplotlib>=3.7,<4` 반영되어 있음
- (선택) `matplotlib>=3.8,<4`로 업데이트 권장 (Streamlit Cloud 호환성)

---

### Step B. ReflectOS-Android(TWA) 프로젝트 생성

#### B-1. FaithLoop-Android 폴더 복사

**Windows PowerShell:**
```powershell
# ReflectOS_Clean 폴더에서 실행
Copy-Item -Path "FaithLoop_extracted\FaithLoop-Android" -Destination "ReflectOS-Android" -Recurse
cd ReflectOS-Android
```

**또는 수동으로:**
- `FaithLoop_extracted/FaithLoop-Android` 폴더 전체를 복사
- `ReflectOS-Android`로 이름 변경

#### B-2. `app/build.gradle` 수정

**변경할 값들:**

```gradle
def twaManifest = [
    applicationId: 'com.reflectos.app',  // 변경: com.faithloop.app → com.reflectos.app
    hostName: 'reflectos.streamlit.app',  // 변경: faithloop.streamlit.app → reflectos.streamlit.app
    launchUrl: '/',
    name: 'ReflectOS',  // 변경: FaithLoop → ReflectOS
    launcherName: 'ReflectOS',  // 변경: FaithLoop → ReflectOS
    themeColor: '#FF6B6B',  // 변경: 원하는 색상
    // ... 기타 설정
]

android {
    namespace "com.reflectos.app"  // 변경: com.faithloop.app → com.reflectos.app
    defaultConfig {
        applicationId "com.reflectos.app"  // 변경
        minSdkVersion 21
        targetSdkVersion 35
        versionCode 1  // 변경: 첫 업로드이므로 1부터 가능
        versionName "1.0.0"  // 변경: 원하는 버전
        // ... 기타 설정
    }
    signingConfigs {
        release {
            storeFile file('../android.keystore')  // 또는 reflectos.keystore
            keyAlias "reflectos"  // 변경: faithloop → reflectos (새 keystore 사용 시)
            // ... 기타 설정
        }
    }
}
```

**전체 파일 예시:** [android/app/build.gradle.example](../android/app/build.gradle.example) 참고

#### B-3. `app/src/main/AndroidManifest.xml` 수정

**package 속성 확인:**
```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.reflectos.app">  <!-- 변경: com.faithloop.app → com.reflectos.app -->
```

**참고:** AGP 8.x에서는 `namespace`가 `build.gradle`에서 관리되지만, `package` 속성은 경로 참조용으로 필요합니다.

**전체 파일 예시:** [android/app/src/main/AndroidManifest.xml.example](../android/app/src/main/AndroidManifest.xml.example) 참고

#### B-4. `twa-manifest.json` 수정 (프로젝트 루트)

```json
{
  "packageId": "com.reflectos.app",  // 변경
  "host": "reflectos.streamlit.app",  // 변경
  "name": "ReflectOS",  // 변경
  "launcherName": "ReflectOS",  // 변경
  "appVersionCode": 1,  // 변경: 첫 업로드
  "appVersionName": "1.0.0",  // 변경
  "signingKey": {
    "alias": "reflectos"  // 변경: faithloop → reflectos
  },
  "webManifestUrl": "https://reflectos.streamlit.app/manifest.json",  // 변경
  "fullScopeUrl": "https://reflectos.streamlit.app/",  // 변경
  // ... 기타 설정
}
```

---

### Step C. assetStatements / 사이트 URL 문자열 교체

#### C-1. `app/src/main/res/values/strings.xml` 수정

**변경 전:**
```xml
<string name="assetStatements">
  [{
      \"relation\": [\"delegate_permission/common.handle_all_urls\"],
      \"target\": {
          \"namespace\": \"web\",
          \"site\": \"https://faithloop.streamlit.app\"  <!-- 변경 필요 -->
      }
  }]
</string>
```

**변경 후:**
```xml
<string name="assetStatements">
  [{
      \"relation\": [\"delegate_permission/common.handle_all_urls\"],
      \"target\": {
          \"namespace\": \"web\",
          \"site\": \"https://reflectos.streamlit.app\"  <!-- 변경 완료 -->
      }
  }]
</string>
```

#### C-2. 전체 프로젝트에서 faithloop → reflectos 교체

**검색 및 교체:**
- `faithloop.streamlit.app` → `reflectos.streamlit.app`
- `com.faithloop.app` → `com.reflectos.app` (이미 build.gradle에서 변경)
- `FaithLoop` → `ReflectOS` (화면 표시용)

**주의:** 
- Streamlit 기본 도메인은 `.well-known/assetlinks.json`을 직접 올리기 어려워서 완전 "Trusted"가 아닐 수 있음
- 그래도 FaithLoop에서 이미 같은 방식으로 진행했으니 동일 전략으로 우선 진행
- 나중에 "주소창 숨김(완전 TWA)"까지 원하면 커스텀 도메인(가비아) + assetlinks.json 호스팅으로 업그레이드

---

### Step D. 서명키(keystore) 전략 결정

#### D-1. 빠른 길 (권장X/가능O): FaithLoop keystore 재사용

**장점:** 빠르게 시작 가능
**단점:** 두 앱이 같은 keystore 공유 (보안상 권장하지 않음)

**사용 방법:**
```gradle
signingConfigs {
    release {
        storeFile file('../android.keystore')  // FaithLoop keystore 사용
        keyAlias "faithloop"  // 기존 alias 사용
        // ... 기타 설정
    }
}
```

#### D-2. 안전한 길 (권장): ReflectOS 전용 keystore 생성

**새 keystore 생성:**
```bash
keytool -genkey -v -keystore reflectos.keystore \
  -keyalg RSA -keysize 2048 -validity 10000 \
  -alias reflectos
```

**정보 입력:**
- 이름, 조직 등 입력
- 비밀번호 기록 (나중에 필요)

**build.gradle 설정:**
```gradle
signingConfigs {
    release {
        storeFile file('../reflectos.keystore')  // 새 keystore 사용
        keyAlias "reflectos"  // 새 alias
        storePassword System.getenv("KEYSTORE_PASSWORD") ?: project.findProperty("KEYSTORE_PASSWORD") ?: ""
        keyPassword System.getenv("KEY_PASSWORD") ?: project.findProperty("KEY_PASSWORD") ?: ""
    }
}
```

---

### Step E. 빌드/검증

#### E-1. 환경변수 설정 (Windows PowerShell)

```powershell
$env:KEYSTORE_PASSWORD='your-keystore-password'
$env:KEY_ALIAS='reflectos'  # 또는 faithloop (재사용 시)
$env:KEY_PASSWORD='your-key-password'
```

#### E-2. 빌드 실행

**프로젝트 루트에서:**
```powershell
.\gradlew.bat clean bundleRelease
```

**또는:**
```bash
./gradlew clean bundleRelease
```

#### E-3. 결과 AAB 경로 확인

**일반적인 경로:**
```
app\build\outputs\bundle\release\app-release.aab
```

**확인 사항:**
- 파일 크기: 보통 5-15MB
- 생성 시간: 최근 시간인지 확인

#### E-4. 서명 확인 (선택)

```bash
keytool -printcert -jarfile app\build\outputs\bundle\release\app-release.aab
```

**확인 사항:**
- 서명 정보 표시
- keystore alias 확인

---

### Step F. Google Play Console(새 앱) 등록

#### F-1. 새 앱 만들기

1. [Google Play Console](https://play.google.com/console) 접속
2. **"앱 만들기"** 클릭
3. **"새 앱"** 선택
4. 앱 정보 입력:
   - **앱 이름**: ReflectOS
   - **기본 언어**: 한국어
   - **앱 또는 게임**: 앱
   - **무료 또는 유료**: 무료

#### F-2. 테스트 트랙 선택

**권장: 비공개 테스트 (Closed testing)**
- 처음부터 **비공개 테스트**로 시작
- FaithLoop에서 내부 테스트 → 비공개 전환 시 versionCode 충돌 경험했으므로, ReflectOS는 처음부터 비공개로 시작

#### F-3. AAB 업로드

1. 선택한 테스트 트랙에서 **"새 버전 만들기"** 클릭
2. **"앱 번들 업로드"** 클릭
3. `app-release.aab` 파일 선택
4. 업로드 완료 대기

**오류 처리:**
- "버전코드 이미 사용됨" 오류 발생 시:
  - `build.gradle`에서 `versionCode` +1 증가
  - 재빌드 후 다시 업로드

#### F-4. 최소 필수 정보 작성

**필수 항목:**
- 테스터 목록 (최소 1명)
- 데이터 안전 (기본 정보)
- 개인정보처리방침 URL (선택)
- 스토어 등록정보 (최소 정보)

**참고:** 테스트 트랙에서는 최소 정보만 입력해도 배포 가능

---

## ✅ 최종 확인 체크리스트

### 독립성 확인
- [ ] **패키지명**: `com.reflectos.app` (FaithLoop: `com.faithloop.app`)
- [ ] **호스트명**: `reflectos.streamlit.app` (FaithLoop: `faithloop.streamlit.app`)
- [ ] **앱 이름**: ReflectOS (FaithLoop: FaithLoop)
- [ ] **Play Console 앱**: 새로 생성된 앱 (FaithLoop와 별개)

### 버전 관리
- [ ] ReflectOS 첫 업로드: `versionCode = 1`
- [ ] 같은 앱 내에서만 증가 규칙 적용

### 설정 파일 확인
- [ ] `app/build.gradle`: 모든 ReflectOS 값으로 변경
- [ ] `app/src/main/AndroidManifest.xml`: package 속성 변경
- [ ] `app/src/main/res/values/strings.xml`: assetStatements site URL 변경
- [ ] `twa-manifest.json`: 모든 ReflectOS 값으로 변경

### 빌드 확인
- [ ] AAB 빌드 성공
- [ ] 서명 확인 완료

### Play Console 확인
- [ ] 새 앱 생성 완료
- [ ] AAB 업로드 성공
- [ ] 테스트 트랙 설정 완료

---

## 🔗 관련 문서

- [ReflectOS Android 프로젝트 설정 가이드](./REFLECTOS_ANDROID_SETUP.md)
- [Android TWA 배포 가이드](./DEPLOY_ANDROID_TWA.md)
- [배포 체크리스트](./DEPLOY_CHECKLIST.md)
