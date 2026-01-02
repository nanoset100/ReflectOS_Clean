# ReflectOS 🪞

> 개인 회고 & 시간 관리 MVP - Streamlit 기반

## 핵심 기능

- 📝 **멀티모달 입력**: 텍스트, 이미지, 음성으로 일상 기록
- 🧠 **RAG 기반 회고**: AI가 과거 기록을 참조하여 통찰 제공
- 📊 **주간 리포트**: 자동 생성되는 주간 회고 리포트
- 📅 **시간블록 플래너**: 하루 일정을 시간 블록으로 계획
- 🔗 **Google Calendar 연동**: 양방향 일정 동기화

## 기술 스택

| 영역 | 기술 |
|------|------|
| Frontend | Streamlit (multipage) |
| Database | Supabase Postgres + pgvector |
| Storage | Supabase Storage |
| AI | OpenAI (GPT-4, Embeddings, Whisper) |
| Calendar | Google Calendar API (OAuth2) |

## 설치 및 실행

### 1. 가상환경 생성

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. Secrets 설정

`.streamlit/secrets.toml` 파일을 생성하고 필요한 키를 설정합니다:

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# 이후 secrets.toml을 편집하여 실제 키 입력
```

### 4. Supabase 스키마 적용

Supabase 대시보드 SQL Editor에서 `sql/schema.sql` 실행

### 5. 앱 실행

```bash
streamlit run reflectos/app.py
```

## 폴더 구조

```
/reflectos
  app.py              # 메인 엔트리
  /pages              # Streamlit 멀티페이지
    1_Home.py
    2_Checkin.py
    3_Report.py
    4_Planner.py
    5_Memory.py
    6_Settings.py
  /lib                # 유틸리티 모듈
    config.py         # 설정 로드
    supabase_db.py    # DB CRUD 헬퍼
    supabase_storage.py
    openai_client.py
    rag.py
    calendar_google.py
    prompts.py
    utils.py
  /sql
    schema.sql        # DB 스키마
  requirements.txt
  .streamlit/
    secrets.toml.example
```

## 개발 로드맵

- [x] Step 0: 프로젝트 부팅
- [x] Step 1: Supabase 연결 + 스키마
- [ ] Step 2: 체크인 입력 (텍스트)
- [ ] Step 3: 멀티모달 입력 (이미지/음성)
- [ ] Step 4: RAG 기반 회고
- [ ] Step 5: 주간 리포트
- [ ] Step 6: 시간블록 플래너
- [ ] Step 7: Google Calendar 연동

