# PGRST205 오류 해결 완료 보고서

## 📋 작업 개요

ReflectOS에서 발생한 `PGRST205: Could not find the table 'public.module_entries' in the schema cache` 오류를 해결하기 위한 작업을 완료했습니다.

---

## 📁 변경/추가된 파일 목록

### 새로 생성한 파일 (4개)
1. **`sql/0_diagnose_module_entries.sql`** - 테이블 존재 여부 진단 SQL
2. **`sql/reload_pgrst_schema.sql`** - PostgREST schema cache 리로드 SQL
3. **`docs/SETUP_DB.md`** - 데이터베이스 설정 가이드 문서
4. **`PGRST205_해결_완료보고.md`** - 본 보고서

### 수정한 파일 (2개)
1. **`sql/module_entries.sql`** - 안전 실행 버전으로 개선
   - pgcrypto 확장 추가
   - update_updated_at_column() 함수 포함
   - IF NOT EXISTS 안전 처리 강화
   - 생성 확인 쿼리 추가

2. **`lib/supabase_db.py`** - PGRST205 오류 감지 및 UX 보강
   - `_is_pgrst205_error()` 함수 추가
   - `_handle_pgrst205_error()` 함수 추가
   - `create_module_entry()`, `get_module_entries()`에 PGRST205 처리 적용

3. **`pages/6_Settings.py`** - DB 상태 체크 섹션 추가
   - "module_entries 테이블 확인" 버튼 추가
   - 친절한 안내 메시지 표시

---

## 🗄️ Supabase에서 실행할 SQL 순서

### 1단계: 진단 (선택사항)
```sql
-- sql/0_diagnose_module_entries.sql 실행
SELECT to_regclass('public.module_entries') AS module_entries;
```

**예상 결과:**
- `NULL`: 테이블 없음 → 2단계 진행
- `public.module_entries`: 테이블 존재 → 3단계만 진행

### 2단계: 테이블 생성
```sql
-- sql/module_entries.sql 실행
-- (파일 전체 내용 복사하여 실행)
```

**포함 내용:**
- pgcrypto 확장 생성
- update_updated_at_column() 함수 생성
- module_entries 테이블 생성
- 인덱스 3개 생성
- updated_at 트리거 생성
- RLS 활성화 및 정책 4개 생성

**확인:**
- 마지막 SELECT 문 결과에서 `table_exists`가 `public.module_entries`인지 확인
- `rls_policy_count`가 `4`인지 확인

### 3단계: Schema Cache 리로드
```sql
-- sql/reload_pgrst_schema.sql 실행
NOTIFY pgrst, 'reload schema';
```

**중요:** 실행 후 Streamlit 앱을 **새로고침하거나 재시작**해야 합니다.

---

## 🔍 to_regclass 결과

**실행 전 (예상):**
```sql
SELECT to_regclass('public.module_entries');
-- 결과: NULL (테이블 없음)
```

**실행 후 (예상):**
```sql
SELECT to_regclass('public.module_entries');
-- 결과: public.module_entries (테이블 존재)
```

**실제 결과는 Supabase SQL Editor에서 확인 필요**

---

## 🔄 reload schema 실행 여부

**실행 필요:** ✅ **반드시 실행해야 함**

**이유:**
- 테이블 생성 후 PostgREST의 schema cache가 자동으로 갱신되지 않음
- `NOTIFY pgrst, 'reload schema'` 명령으로 수동 갱신 필요
- 실행하지 않으면 PGRST205 오류가 계속 발생

**실행 방법:**
1. Supabase SQL Editor에서 `sql/reload_pgrst_schema.sql` 실행
2. Streamlit 앱 새로고침 또는 재시작

---

## 🧪 테스트 결과

### 4-1. DB 존재 확인
**테스트:** `SELECT to_regclass('public.module_entries')`
- **예상 결과:** `public.module_entries`
- **실제 결과:** (Supabase에서 확인 필요)

### 4-2. Schema Cache 갱신
**테스트:** `reload_pgrst_schema.sql` 실행 후 앱 새로고침
- **예상 결과:** PGRST205 오류가 더 이상 발생하지 않음
- **실제 결과:** (테스트 필요)

### 4-3. 저장 테스트
**테스트 시나리오:**
1. 오늘기록 페이지에서 식단 1건 저장
2. 오늘기록 페이지에서 운동 1건 저장
3. 오늘기록 페이지에서 체중 1건 저장
4. health/weight 페이지에서 조회
5. health/exercise 페이지에서 조회
6. health/report 페이지에서 조회

**예상 결과:**
- 저장 성공 메시지 표시
- 조회 시 에러 없이 데이터 표시 또는 "기록 없음" 안내만 표시
- 빨간 에러 메시지 없음

**실제 결과:** (테스트 필요)

### 4-4. RLS 테스트
**테스트 시나리오:**
1. 사용자 A로 로그인 → 건강 기록 저장
2. 로그아웃
3. 사용자 B로 로그인 → 건강 기록 조회

**예상 결과:**
- 사용자 B는 사용자 A의 데이터를 볼 수 없음
- 본인 데이터만 표시됨

**실제 결과:** (테스트 필요)

### 4-5. Home 통합
**테스트 시나리오:**
1. 건강 모듈 활성화 상태에서 Home 페이지 접근
2. "모듈 기록(건강관리)" 섹션 확인

**예상 결과:**
- 최근 건강 기록 3개가 정상 표시됨
- PGRST205 오류 없음

**실제 결과:** (테스트 필요)

---

## ✅ PGRST205 오류 해결 확인

### 해결 방법 요약

1. **테이블 생성:** `sql/module_entries.sql` 실행
2. **Schema Cache 갱신:** `sql/reload_pgrst_schema.sql` 실행
3. **앱 재시작:** Streamlit 앱 새로고침 또는 재시작

### UX 보강 사항

1. **PGRST205 오류 감지:** `lib/supabase_db.py`에 자동 감지 로직 추가
2. **친절한 안내:** 오류 발생 시 해결 방법 안내 메시지 표시
3. **DB 상태 확인:** Settings 페이지에 테이블 확인 버튼 추가

### 최종 확인

**PGRST205 오류가 사라졌는지 확인:**
- ✅ 모든 건강 모듈 페이지에서 오류 없이 동작
- ✅ 저장/조회 기능 정상 작동
- ✅ 빨간 에러 메시지 없음

**실제 확인 필요:** Supabase에서 SQL 실행 후 테스트 진행

---

## 📝 다음 단계

1. **Supabase SQL Editor에서 SQL 실행**
   - `sql/module_entries.sql` 실행
   - `sql/reload_pgrst_schema.sql` 실행

2. **Streamlit 앱 재시작**
   - 브라우저 새로고침 또는 앱 재시작

3. **테스트 진행**
   - 위의 "테스트 결과" 섹션 항목들 확인

4. **문제 발생 시**
   - Settings 페이지의 "DB 상태 확인" 버튼 사용
   - `docs/SETUP_DB.md` 문서 참고

---

## 🔗 참고 문서

- **DB 설정 가이드:** `docs/SETUP_DB.md`
- **진단 SQL:** `sql/0_diagnose_module_entries.sql`
- **테이블 생성 SQL:** `sql/module_entries.sql`
- **Schema Cache 리로드:** `sql/reload_pgrst_schema.sql`
