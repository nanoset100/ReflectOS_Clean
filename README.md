# ReflectOS 🪞

> **개인 회고 & 시간 관리** — Streamlit 기반 MVP  
> 일상 기록, AI 회고, 주간 리포트, 시간블록 플래너, RAG 검색까지 한곳에서.

---

## 목차

- [개요](#개요)
- [앱 구조](#앱-구조)
- [기능](#기능)
- [기술 스택](#기술-스택)
- [데이터베이스](#데이터베이스)
- [API](#api)
- [설치 및 실행](#설치-및-실행)
- [배포](#배포)
- [관련 문서](#관련-문서)
- [로드맵](#로드맵)

---

## 개요

ReflectOS는 **일상 체크인 → AI 구조화 → RAG 기반 회고/검색 → 주간 리포트/플래너**까지 이어지는 개인용 회고·시간관리 앱이다.

- **인증**: Supabase Auth (이메일/비밀번호, 로그인·회원가입·세션)
- **프론트**: Streamlit multipage + `st.navigation`
- **모듈**: 공통(홈/체크인/리포트/플래너/메모리) + 선택 모듈(건강·수험생·취준생)
- **백엔드**: Supabase(Postgres + Storage) + 선택적 FastAPI 서버

---

## 앱 구조

```
ReflectOS_Clean/
├── app.py                    # 메인 엔트리 — 인증 게이트, 네비게이션 구성
├── requirements.txt
│
├── pages/                     # Streamlit 페이지
│   ├── 1_Home.py              # 대시보드 — 오늘 일정, 최근 체크인
│   ├── 2_Checkin.py           # 체크인 — 텍스트/음성/이미지 기록, 규칙·LLM 추출
│   ├── 3_Report.py            # 주간 리포트 — wins/issues/patterns/next_experiments
│   ├── 4_Planner.py           # 시간블록 플래너 — AI 제안, 타임라인
│   ├── 5_Memory.py            # RAG 검색 — 벡터 검색 + AI 답변
│   ├── 6_Settings.py          # 설정 — Supabase/OpenAI/Google Calendar, 모듈 on/off
│   ├── auth.py                # (미사용 시 삭제 가능) 인증 UI 공용
│   │
│   ├── health/                # 건강 모듈 (설정에서 활성화 시 노출)
│   │   ├── today.py           # 오늘 기록 — 식단/운동/체중
│   │   ├── weight.py          # 체중
│   │   ├── exercise.py        # 운동
│   │   └── report.py          # 건강 리포트
│   │
│   ├── student/                # 수험생 모듈
│   │   ├── today.py           # 오늘 학습 — 과목·시간·집중도
│   │   ├── subjects.py        # 과목 목표
│   │   ├── coaching.py        # 슬럼프 로그
│   │   └── report.py          # 학습 리포트
│   │
│   └── jobseeker/             # 취준생 모듈
│       ├── tracker.py         # 지원 현황
│       ├── interview.py       # 면접 기록
│       ├── resume.py          # 이력서 관리
│       └── report.py          # 취준 리포트
│
├── lib/                       # 공용 라이브러리
│   ├── auth.py                # Supabase Auth — 로그인/회원가입/로그아웃/세션
│   ├── auth_ui.py             # 로그인·회원가입 UI
│   ├── config.py              # st.secrets 로드 — Supabase, OpenAI, Google
│   ├── modules.py             # 모듈 레지스트리(health/student/jobseeker) + 활성 모듈 조회/저장
│   ├── module_ui.py           # 모듈 선택 UI (Settings에서 사용)
│   ├── supabase_db.py         # DB CRUD — checkins, profiles, plans, module_entries 등
│   ├── supabase_storage.py    # Storage 업로드/다운로드
│   ├── openai_client.py       # OpenAI — 채팅, JSON 모드, 임베딩
│   ├── rag.py                 # RAG — 청크/임베딩·검색
│   ├── prompts.py             # 시스템/유저 프롬프트 문자열
│   ├── calendar_google.py     # Google Calendar OAuth + 오늘 일정
│   ├── demo_data.py           # 데모 데이터
│   └── utils.py               # 공용 유틸
│
├── api/                       # FastAPI (선택 사용)
│   ├── main.py                # 앱 진입, CORS, 라우터 등록
│   └── routers/
│   │   ├── health.py          # GET /health
│   │   ├── checkins.py        # POST/GET /checkins
│   │   ├── memory.py          # POST /memory/search
│   │   └── report.py         # GET /report/weekly
│   └── schemas.py             # Pydantic 스키마
│
├── sql/                       # Supabase에서 실행할 SQL
│   ├── schema.sql             # 기본 스키마 — profiles, checkins, plans, memory_embeddings 등
│   ├── module_entries.sql     # module_entries 테이블 + RLS
│   ├── reload_pgrst_schema.sql
│   └── ...
│
├── android/                   # Android TWA용 예시 설정
│   └── *.example
│
├── docs/                      # 배포·설정 가이드
│   ├── SETUP_DB.md
│   ├── DEPLOY_STREAMLIT_CLOUD.md
│   ├── STREAMLIT_CLOUD_SECRETS.md
│   ├── DEPLOY_ANDROID_TWA.md
│   └── ...
│
└── .streamlit/
    └── secrets.toml.example  # 복사 후 secrets.toml 로 실제 키 입력
```

---

## 기능

### 공통 (항상 표시)

| 페이지 | 설명 |
|--------|------|
| **Home** | 오늘 Google Calendar 일정, 최근 체크인 목록, Supabase 연결 상태 |
| **Check-in** | 일상 기록 입력(텍스트/음성/이미지). 규칙 기반·LLM 추출(tasks/obstacles/projects/insights). 저장 시 선택적으로 메모리 인덱싱 |
| **Report** | 주간 체크인·추출 데이터 기반 AI 주간 리포트(summary, wins, issues, patterns, next_experiments, mood_analysis) |
| **Planner** | 오늘 목표·근무시간·기존 일정 입력 → AI 시간블록 제안. 카테고리(업무/회의/건강/자기계발/휴식/생활) |
| **Memory** | 질문 입력 → pgvector 유사도 검색 → 검색 결과를 컨텍스트로 AI 답변. 검색 수·임계값·데모 제외 옵션 |
| **Settings** | Supabase / OpenAI / Google Calendar 연결 상태, OAuth 콜백 처리, 모듈 on/off, DB 상태 확인 |

### 선택 모듈 (Settings에서 활성화 시 사이드에만 표시)

| 모듈 | 페이지 | 요약 |
|------|--------|------|
| **건강** | 오늘 기록, 체중, 운동, 건강 리포트 | 식단/운동/체중을 `module_entries`(module=health)에 기록 |
| **수험생** | 오늘 학습, 과목 목표, 슬럼프 로그, 학습 리포트 | 학습 세션·과목·집중도 등 (module=student) |
| **취준생** | 지원 현황, 면접 기록, 이력서 관리, 취준 리포트 | 회사/직무/상태/면접 내용 등 (module=jobseeker) |

모듈 데이터는 공통 테이블 `module_entries`(user_id, module, entry_type, occurred_on, payload, tags, metadata)에 저장된다.

---

## 기술 스택

| 구분 | 기술 |
|------|------|
| **Frontend** | Streamlit (multipage, st.navigation) |
| **인증** | Supabase Auth |
| **DB** | Supabase Postgres + pgvector |
| **Storage** | Supabase Storage |
| **AI** | OpenAI (GPT, Embeddings, Whisper) |
| **캘린더** | Google Calendar API (OAuth2) |
| **API 서버** | FastAPI + Uvicorn (선택) |

---

## 데이터베이스

Supabase에 아래 순서로 적용한다.

1. **기본 스키마** — `sql/schema.sql`  
   - `profiles`, `checkins`, `artifacts`, `extractions`, `calendar_events`, `plans`, `plan_blocks`, `memory_chunks`, `memory_embeddings`  
   - RAG용 `search_memories(query_embedding, match_count, match_threshold, user_id_filter)` 함수  
   - RLS, `updated_at` 트리거
2. **모듈용 테이블** — `sql/module_entries.sql`  
   - `module_entries` (module ∈ `student`, `jobseeker`, `health`)  
   - RLS: 본인 행만 select/insert/update/delete
3. **PostgREST 스키마 갱신** — `sql/reload_pgrst_schema.sql` (필요 시)

자세한 단계는 [docs/SETUP_DB.md](docs/SETUP_DB.md) 참고.

---

## API

FastAPI 앱은 별도 프로세스로 띄우며, Streamlit은 기본적으로 Supabase를 직접 사용한다.

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/` | API 이름·버전·docs 경로 |
| GET | `/health` | 헬스체크 |
| POST | `/checkins` | 체크인 생성 (스키마 기준) |
| GET | `/checkins` | 체크인 목록 |
| POST | `/memory/search` | RAG 검색 |
| GET | `/report/weekly` | 주간 리포트 |

실행 예: `uvicorn api.main:app --reload --host 0.0.0.0 --port 8000`

---

## 설치 및 실행

### 1. 가상환경

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 2. 의존성

```bash
pip install -r requirements.txt
```

### 3. Secrets

`.streamlit/secrets.toml`을 만들고 아래처럼 설정한다. 예시는 `.streamlit/secrets.toml.example` 참고.

```toml
[supabase]
url = "https://your-project.supabase.co"
key = "your-anon-key"

[openai]
api_key = "sk-..."

[google]
client_id = "....apps.googleusercontent.com"
client_secret = "..."
redirect_uri = "http://localhost:8501"
```

### 4. DB 설정

Supabase SQL Editor에서 `sql/schema.sql` → `sql/module_entries.sql` 순서로 실행. 자세한 절차는 [docs/SETUP_DB.md](docs/SETUP_DB.md).

### 5. 앱 실행

```bash
streamlit run app.py
```

브라우저에서 `http://localhost:8501` 접속.

---

## 배포

- **Streamlit Cloud**  
  - [배포 가이드](docs/DEPLOY_STREAMLIT_CLOUD.md)  
  - [Secrets 설정](docs/STREAMLIT_CLOUD_SECRETS.md)
- **Android TWA**  
  - [Android TWA 배포](docs/DEPLOY_ANDROID_TWA.md)  
  - [배포 체크리스트](docs/DEPLOY_CHECKLIST.md)

---

## 관련 문서

| 문서 | 내용 |
|------|------|
| [SETUP_DB.md](docs/SETUP_DB.md) | DB 스키마·module_entries·RLS 적용 순서 |
| [DEPLOY_STREAMLIT_CLOUD.md](docs/DEPLOY_STREAMLIT_CLOUD.md) | Streamlit Cloud 배포 |
| [STREAMLIT_CLOUD_SECRETS.md](docs/STREAMLIT_CLOUD_SECRETS.md) | 클라우드용 Secrets |
| [DEPLOY_ANDROID_TWA.md](docs/DEPLOY_ANDROID_TWA.md) | Android TWA 빌드·배포 |
| [DEPLOY_CHECKLIST.md](docs/DEPLOY_CHECKLIST.md) | 배포 전 점검 목록 |

---

## 로드맵

- [x] 프로젝트 부팅
- [x] Supabase 연결 및 기본 스키마
- [x] Supabase Auth 인증(로그인/회원가입/세션)
- [x] 모듈 시스템(건강/수험생/취준생) 및 `module_entries`
- [x] 체크인 규칙·LLM 추출, 주간 리포트, RAG Memory, 시간블록 Planner
- [x] Google Calendar 연동(오늘 일정, Settings OAuth)
- [ ] 멀티모달 입력 고도화(음성 STT/이미지 Vision 안정화)
- [ ] FastAPI ↔ Supabase 연동 완료(체크인/메모리/리포트)
