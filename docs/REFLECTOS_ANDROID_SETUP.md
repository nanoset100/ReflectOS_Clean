# ReflectOS-Android 프로젝트 설정 가이드

## 📋 FaithLoop-Android 기반 설정

FaithLoop-Android 프로젝트를 복사하여 ReflectOS-Android로 변환하는 상세 가이드입니다.

---

## 🚀 Step 1: 프로젝트 복사

```bash
# FaithLoop-Android 폴더 복사
cp -r FaithLoop-Android ReflectOS-Android
cd ReflectOS-Android
```

**또는 Windows PowerShell:**
```powershell
Copy-Item -Path "FaithLoop-Android" -Destination "ReflectOS-Android" -Recurse
cd ReflectOS-Android
```

---

## ⚙️ Step 2: build.gradle 수정

### 2-1. `app/build.gradle` 수정

**변경할 값들:**

```gradle
def twaManifest = [
    applicationId: 'com.reflectos.app',  // 변경: com.faithloop.app → com.reflectos.app
    hostName: 'reflectos-xxxx.streamlit.app',  // 변경: Streamlit Cloud URL의 hostname
    launchUrl: '/',
    name: 'ReflectOS',  // 변경: FaithLoop → ReflectOS
    launcherName: 'ReflectOS',  // 변경: FaithLoop → ReflectOS
    themeColor: '#FF6B6B',  // 변경: 원하는 테마 색상 (예: #FF6B6B)
    themeColorDark: '#000000',
    navigationColor: '#000000',
    navigationColorDark: '#000000',
    navigationDividerColor: '#000000',
    navigationDividerColorDark: '#000000',
    backgroundColor: '#FFFFFF',
    enableNotifications: true,
    shortcuts: [],
    splashScreenFadeOutDuration: 300,
    generatorApp: 'bubblewrap-cli',
    fallbackType: 'customtabs',
    enableSiteSettingsShortcut: 'true',
    orientation: 'portrait',
]

android {
    compileSdkVersion 36
    namespace "com.reflectos.app"  // 변경: com.faithloop.app → com.reflectos.app
    defaultConfig {
        applicationId "com.reflectos.app"  // 변경
        minSdkVersion 21
        targetSdkVersion 35
        versionCode 1  // 변경: 첫 업로드면 1
        versionName "1.0.0"  // 변경: 원하는 버전

        // ... 나머지 설정은 그대로 유지
    }
    signingConfigs {
        release {
            storeFile file('../android.keystore')  // keystore 파일 경로
            storePassword System.getenv("KEYSTORE_PASSWORD") ?: project.findProperty("KEYSTORE_PASSWORD") ?: ""
            keyAlias System.getenv("KEY_ALIAS") ?: project.findProperty("KEY_ALIAS") ?: "reflectos"  // 변경: faithloop → reflectos
            keyPassword System.getenv("KEY_PASSWORD") ?: project.findProperty("KEY_PASSWORD") ?: ""
        }
    }
    // ... 나머지 설정은 그대로 유지
}
```

**전체 파일 예시:** [android/app/build.gradle.example](./android/app/build.gradle.example) 참고

---

### 2-2. `build.gradle` (루트) 확인

일반적으로 변경 불필요. 확인만:

```gradle
buildscript {
    repositories {
        google()
        jcenter()
    }
    dependencies {
        classpath 'com.android.tools.build:gradle:8.9.1'
    }
}
```

---

### 2-3. `settings.gradle` 확인

일반적으로 변경 불필요:

```gradle
include ':app'
```

---

### 2-4. `gradle.properties` 확인

일반적으로 변경 불필요:

```properties
org.gradle.jvmargs=-Xmx512m -XX:MaxMetaspaceSize=256m
org.gradle.daemon=true
org.gradle.configureondemand=true
android.useAndroidX=true
android.enableJetifier=true
```

---

## 📝 Step 3: AndroidManifest.xml 수정

### 3-1. `app/src/main/AndroidManifest.xml` 수정

**주의:** FaithLoop에서는 `package="com.faithloop.app"` 속성이 있지만, AGP 8.x에서는 namespace로 관리하므로 **제거하지 않아도 됩니다**. 다만 주석에 명시된 대로 Gradle이 자동으로 처리합니다.

**변경할 값들:**

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.reflectos.app">  <!-- 변경: com.faithloop.app → com.reflectos.app -->
    
    <!-- ... 나머지 설정은 그대로 유지 -->
</manifest>
```

**참고:** 실제로는 `namespace`가 `build.gradle`에서 관리되므로, `package` 속성은 경로 참조용으로만 사용됩니다.

**전체 파일 예시:** [android/app/src/main/AndroidManifest.xml.example](./android/app/src/main/AndroidManifest.xml.example) 참고

---

## 🎨 Step 4: 리소스 파일 수정

### 4-1. 아이콘 교체

**필요한 아이콘:**
- `app/src/main/res/mipmap-xxxhdpi/ic_launcher.png` (192x192)
- `app/src/main/res/mipmap-xxxhdpi/ic_launcher_round.png` (512x512)
- `app/src/main/res/drawable/ic_notification_icon.png` (알림 아이콘)

**교체 방법:**
1. ReflectOS 아이콘 이미지 준비
2. 기존 FaithLoop 아이콘 파일 삭제
3. ReflectOS 아이콘으로 교체

### 4-2. 스플래시 화면 교체

**파일:**
- `app/src/main/res/drawable/splash.xml`

**수정:** 필요시 ReflectOS 브랜딩에 맞게 수정

### 4-3. strings.xml 수정

**파일:** `app/src/main/res/values/strings.xml`

**중요:** `assetStatements`의 `site` 값을 ReflectOS URL로 변경해야 합니다:

```xml
<string name="assetStatements">
  [{
      \"relation\": [\"delegate_permission/common.handle_all_urls\"],
      \"target\": {
          \"namespace\": \"web\",
          \"site\": \"https://reflectos-xxxx.streamlit.app\"  <!-- 변경: faithloop.streamlit.app → reflectos-xxxx.streamlit.app -->
      }
  }]
</string>
```

**예시 파일:** [android/app/src/main/res/values/strings.xml.example](./android/app/src/main/res/values/strings.xml.example) 참고

**참고:** 나머지 strings는 `build.gradle`의 `resValue`로 자동 생성되므로 수동 수정 불필요.

---

## 🔐 Step 5: Keystore 설정

### 5-1. 기존 keystore 재사용 (권장)

FaithLoop의 keystore를 그대로 사용 가능:

```bash
# keystore 파일이 프로젝트 루트에 있는 경우
# android.keystore 파일을 그대로 사용
```

**build.gradle 설정:**
```gradle
signingConfigs {
    release {
        storeFile file('../android.keystore')
        keyAlias "reflectos"  // 또는 기존 alias 사용
    }
}
```

### 5-2. 새 keystore 생성 (선택)

```bash
keytool -genkey -v -keystore reflectos-release-key.jks \
  -keyalg RSA -keysize 2048 -validity 10000 \
  -alias reflectos-key
```

**정보 입력:**
- 이름, 조직 등 입력
- 비밀번호 기록

---

## 📦 Step 6: twa-manifest.json 수정

**파일:** `twa-manifest.json` (프로젝트 루트)

```json
{
  "packageId": "com.reflectos.app",  // 변경
  "host": "reflectos-xxxx.streamlit.app",  // 변경: Streamlit Cloud URL의 hostname
  "name": "ReflectOS",  // 변경
  "launcherName": "ReflectOS",  // 변경
  "display": "standalone",
  "themeColor": "#FF6B6B",  // 변경: 원하는 색상
  "themeColorDark": "#000000",
  "navigationColor": "#000000",
  "navigationColorDark": "#000000",
  "navigationDividerColor": "#000000",
  "navigationDividerColorDark": "#000000",
  "backgroundColor": "#FFFFFF",
  "enableNotifications": true,
  "startUrl": "/",
  "iconUrl": "http://localhost:8000/icon-512.png",  // 개발용, 배포 시 실제 URL로 변경
  "splashScreenFadeOutDuration": 300,
  "signingKey": {
    "path": "M:\\MyProject777\\ReflectOS-Android\\android.keystore",  // 변경: 경로 수정
    "alias": "reflectos"  // 변경: faithloop → reflectos
  },
  "appVersionName": "1.0.0",  // 변경
  "appVersionCode": 1,  // 변경: 첫 업로드면 1
  "shortcuts": [],
  "generatorApp": "bubblewrap-cli",
  "webManifestUrl": "https://reflectos-xxxx.streamlit.app/manifest.json",  // 변경: 실제 URL
  "fallbackType": "customtabs",
  "features": {},
  "alphaDependencies": {
    "enabled": false
  },
  "enableSiteSettingsShortcut": true,
  "isChromeOSOnly": false,
  "isMetaQuest": false,
  "fullScopeUrl": "https://reflectos-xxxx.streamlit.app/",  // 변경: 실제 URL
  "minSdkVersion": 21,
  "orientation": "portrait",
  "fingerprints": [],
  "additionalTrustedOrigins": [],
  "retainedBundles": [],
  "protocolHandlers": [],
  "fileHandlers": [],
  "launchHandlerClientMode": "",
  "displayOverride": [],
  "appVersion": "1.0.0"  // 변경
}
```

---

## ✅ Step 7: 변경 사항 체크리스트

### 필수 변경 사항

- [ ] `app/build.gradle`:
  - [ ] `twaManifest.applicationId = 'com.reflectos.app'`
  - [ ] `twaManifest.hostName = 'reflectos-xxxx.streamlit.app'`
  - [ ] `twaManifest.name = 'ReflectOS'`
  - [ ] `twaManifest.launcherName = 'ReflectOS'`
  - [ ] `namespace = "com.reflectos.app"`
  - [ ] `applicationId = "com.reflectos.app"`
  - [ ] `versionCode = 1` (첫 업로드)
  - [ ] `versionName = "1.0.0"`
  - [ ] `keyAlias = "reflectos"` (또는 기존 alias)

- [ ] `app/src/main/AndroidManifest.xml`:
  - [ ] `package="com.reflectos.app"` (경로 참조용)

- [ ] `twa-manifest.json`:
  - [ ] `packageId = "com.reflectos.app"`
  - [ ] `host = "reflectos-xxxx.streamlit.app"`
  - [ ] `name = "ReflectOS"`
  - [ ] `launcherName = "ReflectOS"`
  - [ ] `appVersionCode = 1`
  - [ ] `appVersionName = "1.0.0"`
  - [ ] `signingKey.alias = "reflectos"`
  - [ ] `webManifestUrl = "https://reflectos-xxxx.streamlit.app/manifest.json"`
  - [ ] `fullScopeUrl = "https://reflectos-xxxx.streamlit.app/"`

- [ ] `app/src/main/res/values/strings.xml`:
  - [ ] `assetStatements`의 `site` 값을 `https://reflectos-xxxx.streamlit.app`로 변경

- [ ] 리소스:
  - [ ] 아이콘 교체 (ic_launcher.png 등)
  - [ ] 스플래시 화면 교체 (선택)

---

## 🔧 Step 8: 빌드 및 테스트

### 8-1. 환경변수 설정 (Windows PowerShell)

```powershell
$env:KEYSTORE_PASSWORD='your-keystore-password'
$env:KEY_ALIAS='reflectos'  # 또는 기존 alias
$env:KEY_PASSWORD='your-key-password'
```

### 8-2. 빌드 실행

```bash
# Windows
.\gradlew.bat clean bundleRelease

# macOS/Linux
./gradlew clean bundleRelease
```

### 8-3. 빌드 결과 확인

**AAB 파일 위치:**
```
app/build/outputs/bundle/release/app-release.aab
```

---

## 📤 Step 9: Play Console 업로드

1. Play Console에서 **새 앱** 생성
2. 테스트 트랙 선택: **비공개 테스트 (Closed testing)** 권장
3. AAB 업로드
4. 오류 시 `versionCode` +1 후 재빌드

**자세한 가이드:** [DEPLOY_ANDROID_TWA.md](./DEPLOY_ANDROID_TWA.md) Step 6 참고

---

## 🔗 관련 문서

- [Android TWA 배포 가이드](./DEPLOY_ANDROID_TWA.md)
- [배포 체크리스트](./DEPLOY_CHECKLIST.md)
