-- ============================================
-- profiles 테이블 RLS 정책 강화
-- 기존 "Allow all for anon" 정책 제거 및 본인 행만 접근 가능하도록 변경
-- ============================================

-- 기존 anon 정책 제거
DROP POLICY IF EXISTS "Allow all for anon" ON profiles;

-- RLS 활성화 (이미 되어 있을 수 있음)
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- SELECT 정책: 본인 행만 조회 가능
DROP POLICY IF EXISTS "select own profile" ON profiles;
CREATE POLICY "select own profile"
ON profiles FOR SELECT
TO authenticated
USING (auth.uid()::text = user_id);

-- INSERT 정책: 본인 행만 삽입 가능
DROP POLICY IF EXISTS "insert own profile" ON profiles;
CREATE POLICY "insert own profile"
ON profiles FOR INSERT
TO authenticated
WITH CHECK (auth.uid()::text = user_id);

-- UPDATE 정책: 본인 행만 수정 가능
DROP POLICY IF EXISTS "update own profile" ON profiles;
CREATE POLICY "update own profile"
ON profiles FOR UPDATE
TO authenticated
USING (auth.uid()::text = user_id)
WITH CHECK (auth.uid()::text = user_id);

-- DELETE 정책: 본인 행만 삭제 가능
DROP POLICY IF EXISTS "delete own profile" ON profiles;
CREATE POLICY "delete own profile"
ON profiles FOR DELETE
TO authenticated
USING (auth.uid()::text = user_id);
