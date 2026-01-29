-- ============================================
-- 필수 0: module_entries 테이블 CHECK 제약 확인 및 수정
-- ============================================

-- 1. 테이블 존재 확인
SELECT to_regclass('public.module_entries') AS module_entries;

-- 2. 현재 CHECK 제약 확인
SELECT 
    conname AS constraint_name,
    pg_get_constraintdef(oid) AS constraint_definition
FROM pg_constraint
WHERE conrelid = 'public.module_entries'::regclass
  AND contype = 'c';

-- 3. module 컬럼의 CHECK 제약이 health만 허용하는지 확인
-- 결과에 'health'만 있으면 student/jobseeker 추가 필요

-- 4. student/jobseeker 허용하도록 CHECK 제약 수정
-- (기존 제약이 health만 허용하는 경우)
ALTER TABLE public.module_entries
DROP CONSTRAINT IF EXISTS module_entries_module_check;

ALTER TABLE public.module_entries
ADD CONSTRAINT module_entries_module_check 
CHECK (module IN ('student', 'jobseeker', 'health'));

-- 5. 수정 확인
SELECT 
    conname AS constraint_name,
    pg_get_constraintdef(oid) AS constraint_definition
FROM pg_constraint
WHERE conrelid = 'public.module_entries'::regclass
  AND contype = 'c'
  AND conname LIKE '%module%';

-- 6. RLS 정책 확인
SELECT 
    policyname,
    cmd,
    qual
FROM pg_policies
WHERE tablename = 'module_entries';
