-- ============================================
-- module_entries 테이블 생성 (안전 실행 버전)
-- 공용 모듈 데이터 저장소 (health/student/jobseeker)
-- ============================================

-- pgcrypto 확장 (gen_random_uuid() 사용을 위해)
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- update_updated_at_column() 함수 생성 (안전하게)
-- schema.sql에 있더라도 create or replace로 보장
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 테이블 생성
CREATE TABLE IF NOT EXISTS public.module_entries (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id TEXT NOT NULL,
  module TEXT NOT NULL CHECK (module IN ('student', 'jobseeker', 'health')),
  entry_type TEXT NOT NULL,
  occurred_on DATE NOT NULL,
  payload JSONB NOT NULL DEFAULT '{}',
  tags TEXT[] DEFAULT '{}',
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스 생성 (IF NOT EXISTS는 인덱스에 직접 사용 불가, DROP 후 재생성)
DROP INDEX IF EXISTS idx_module_entries_user_module;
CREATE INDEX idx_module_entries_user_module
  ON public.module_entries(user_id, module);

DROP INDEX IF EXISTS idx_module_entries_occurred_on;
CREATE INDEX idx_module_entries_occurred_on
  ON public.module_entries(occurred_on DESC);

DROP INDEX IF EXISTS idx_module_entries_entry_type;
CREATE INDEX idx_module_entries_entry_type
  ON public.module_entries(entry_type);

-- updated_at 자동 갱신 트리거
DROP TRIGGER IF EXISTS update_module_entries_updated_at ON public.module_entries;
CREATE TRIGGER update_module_entries_updated_at
  BEFORE UPDATE ON public.module_entries
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- RLS (Row Level Security) 정책
-- 절대 금지: anon 전체 허용 정책 (USING true)
-- ============================================

-- RLS 활성화
ALTER TABLE public.module_entries ENABLE ROW LEVEL SECURITY;

-- 기존 정책 제거 (혹시 있을 수 있는 anon 정책 포함)
DROP POLICY IF EXISTS "Allow all for anon" ON public.module_entries;
DROP POLICY IF EXISTS "select own rows" ON public.module_entries;
DROP POLICY IF EXISTS "insert own rows" ON public.module_entries;
DROP POLICY IF EXISTS "update own rows" ON public.module_entries;
DROP POLICY IF EXISTS "delete own rows" ON public.module_entries;

-- SELECT 정책: 본인 행만 조회 가능
CREATE POLICY "select own rows"
ON public.module_entries FOR SELECT
TO authenticated
USING (auth.uid()::text = user_id);

-- INSERT 정책: 본인 행만 삽입 가능
CREATE POLICY "insert own rows"
ON public.module_entries FOR INSERT
TO authenticated
WITH CHECK (auth.uid()::text = user_id);

-- UPDATE 정책: 본인 행만 수정 가능
CREATE POLICY "update own rows"
ON public.module_entries FOR UPDATE
TO authenticated
USING (auth.uid()::text = user_id)
WITH CHECK (auth.uid()::text = user_id);

-- DELETE 정책: 본인 행만 삭제 가능
CREATE POLICY "delete own rows"
ON public.module_entries FOR DELETE
TO authenticated
USING (auth.uid()::text = user_id);

-- 생성 확인
SELECT 
    'module_entries 테이블 생성 완료' AS status,
    to_regclass('public.module_entries') AS table_exists,
    (SELECT COUNT(*) FROM pg_policies WHERE tablename = 'module_entries') AS rls_policy_count;
