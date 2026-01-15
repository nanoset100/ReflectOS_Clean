# ReflectOS 데이터베이스 설정 가이드

## 📋 개요

이 문서는 ReflectOS의 데이터베이스 테이블 및 RLS 정책 설정 방법을 안내합니다.

## ⚠️ 중요 사항

- **모든 SQL은 Supabase SQL Editor에서 실행해야 합니다**
- **실행 순서를 반드시 지켜주세요**
- **각 단계 실행 후 결과를 확인하세요**

---

## 🔍 PHASE 0: 진단 (선택사항)

테이블이 이미 존재하는지 확인하려면:

1. Supabase SQL Editor 열기
2. `sql/0_diagnose_module_entries.sql` 파일 내용 실행
3. 결과 확인:
   - `NULL`: 테이블 없음 → PHASE 1 진행
   - `public.module_entries`: 테이블 존재 → PHASE 2만 진행

---

## 🗄️ PHASE 1: 기본 스키마 설정

### 1-1. 기본 스키마 실행 (최초 설치 시)

**파일:** `sql/schema.sql`

**실행 조건:**
- 최초 설치 시에만 실행
- 이미 profiles, checkins 등 기본 테이블이 있으면 건너뛰기 가능

**실행 방법:**
1. Supabase SQL Editor 열기
2. `sql/schema.sql` 파일 내용 전체 복사
3. 실행 (Run)
4. 에러 없이 완료 확인

---

## 📦 PHASE 2: module_entries 테이블 생성

### 2-1. 테이블 생성

**파일:** `sql/module_entries.sql`

**실행 방법:**
1. Supabase SQL Editor 열기
2. `sql/module_entries.sql` 파일 내용 전체 복사
3. 실행 (Run)
4. 마지막 SELECT 문 결과 확인:
   - `table_exists`: `public.module_entries` 여야 함
   - `rls_policy_count`: `4` 여야 함 (SELECT, INSERT, UPDATE, DELETE)

**포함 내용:**
- ✅ pgcrypto 확장 (gen_random_uuid() 사용)
- ✅ update_updated_at_column() 함수 생성
- ✅ module_entries 테이블 생성
- ✅ 인덱스 3개 생성
- ✅ updated_at 자동 갱신 트리거
- ✅ RLS 활성화
- ✅ RLS 정책 4개 (본인 행만 접근 가능)

---

## 🔄 PHASE 3: PostgREST Schema Cache 리로드

### 3-1. Schema Cache 갱신

**파일:** `sql/reload_pgrst_schema.sql`

**실행 조건:**
- 테이블 생성 직후 **반드시 실행**
- PGRST205 오류가 발생하면 **반드시 실행**

**실행 방법:**
1. Supabase SQL Editor 열기
2. `sql/reload_pgrst_schema.sql` 파일 내용 실행
3. 성공 메시지 확인

**중요:**
- 이 명령은 PostgREST에 스키마 캐시 갱신을 요청합니다
- 실행 후 **Streamlit 앱을 새로고침하거나 재시작**해야 합니다

---

## ✅ 실행 순서 요약

### 최초 설치 시:
```
1. sql/schema.sql 실행
2. sql/module_entries.sql 실행
3. sql/reload_pgrst_schema.sql 실행
4. Streamlit 앱 재시작/새로고침
```

### module_entries만 추가하는 경우:
```
1. sql/module_entries.sql 실행
2. sql/reload_pgrst_schema.sql 실행
3. Streamlit 앱 재시작/새로고침
```

### PGRST205 오류 발생 시:
```
1. sql/reload_pgrst_schema.sql 실행
2. Streamlit 앱 새로고침
3. 여전히 오류면 sql/module_entries.sql 재실행 후 1-2 반복
```

---

## 🧪 검증 방법

### 테이블 존재 확인:
```sql
SELECT to_regclass('public.module_entries') AS module_entries;
-- 결과: public.module_entries (NULL이면 테이블 없음)
```

### RLS 정책 확인:
```sql
SELECT policyname, cmd 
FROM pg_policies 
WHERE tablename = 'module_entries';
-- 결과: 4개 정책 (SELECT, INSERT, UPDATE, DELETE)
```

### 앱에서 확인:
1. Settings 페이지 → "DB 상태 확인" 버튼 클릭
2. ✅ 표시되면 정상
3. ❌ 표시되면 위 SQL 실행 순서 다시 확인

---

## 🐛 문제 해결

### PGRST205 오류가 계속 발생하는 경우:

1. **테이블 존재 확인**
   ```sql
   SELECT to_regclass('public.module_entries');
   ```

2. **테이블이 NULL인 경우**
   - `sql/module_entries.sql` 재실행
   - 에러 메시지 확인

3. **테이블이 있는데도 오류인 경우**
   - `sql/reload_pgrst_schema.sql` 실행
   - Streamlit 앱 완전 재시작 (브라우저 캐시 클리어)

4. **여전히 안 되는 경우**
   - Supabase Dashboard → Database → Tables에서 `module_entries` 확인
   - RLS가 활성화되어 있는지 확인
   - Settings 페이지의 "DB 상태 확인" 사용

---

## 📝 참고사항

- **RLS 정책**: 모든 정책은 `authenticated` 사용자만 접근 가능하며, `auth.uid()::text = user_id` 조건으로 본인 데이터만 접근 가능
- **anon 전체 허용 정책은 절대 만들지 마세요** (보안 위험)
- 테이블 생성 후 반드시 `reload_pgrst_schema.sql` 실행 필요
- Streamlit 앱은 SQL 실행 후 새로고침/재시작 필요
