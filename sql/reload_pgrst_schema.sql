-- ============================================
-- PostgREST schema cache 리로드
-- ============================================
-- 테이블 생성/수정 후 PostgREST가 새로운 스키마를 인식하도록 함

NOTIFY pgrst, 'reload schema';

-- 실행 확인 메시지
SELECT 'PostgREST schema cache 리로드 요청 완료' AS status;

-- 참고:
-- - 이 명령은 PostgREST에 스키마 캐시 갱신을 요청합니다
-- - 테이블 생성 직후 PGRST205 오류가 계속 발생하면 반드시 실행하세요
-- - 실행 후 Streamlit 앱을 새로고침하거나 재시작하세요
