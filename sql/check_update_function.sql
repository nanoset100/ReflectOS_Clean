-- ============================================
-- update_updated_at_column() 함수 존재 확인 및 생성
-- module_entries 트리거를 위해 필요
-- ============================================

-- 함수가 없으면 생성
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 함수 존재 확인 (에러 없으면 성공)
SELECT proname FROM pg_proc WHERE proname = 'update_updated_at_column';
