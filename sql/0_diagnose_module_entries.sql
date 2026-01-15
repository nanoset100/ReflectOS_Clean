-- ============================================
-- PHASE 0: 진단 - module_entries 테이블 존재 확인
-- ============================================
-- Supabase SQL Editor에서 실행하여 테이블 존재 여부 확인

-- 테이블 존재 여부 확인
SELECT to_regclass('public.module_entries') AS module_entries;

-- 결과 해석:
-- - NULL: 테이블이 DB에 없음 (또는 SQL 실행 중 에러로 롤백됨)
-- - public.module_entries: 테이블은 존재하나 schema cache 문제 가능

-- 추가 확인: 테이블 구조 확인 (테이블이 있는 경우)
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_schema = 'public' 
  AND table_name = 'module_entries'
ORDER BY ordinal_position;

-- RLS 정책 확인 (테이블이 있는 경우)
SELECT 
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd,
    qual,
    with_check
FROM pg_policies
WHERE tablename = 'module_entries';
