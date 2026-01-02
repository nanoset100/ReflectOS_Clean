-- ============================================
-- ReflectOS - Database Schema
-- Supabase PostgreSQL + pgvector
-- ============================================

-- pgvector 확장 활성화 (Supabase에서 Extensions에서 활성화 필요)
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================
-- 1. profiles - 사용자 프로필
-- ============================================
CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL UNIQUE,  -- MVP: 단일 사용자 ID 문자열
    display_name TEXT,
    email TEXT,
    timezone TEXT DEFAULT 'Asia/Seoul',
    settings JSONB DEFAULT '{}',  -- 사용자 설정 (알림, 테마 등)
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스
CREATE INDEX IF NOT EXISTS idx_profiles_user_id ON profiles(user_id);

-- ============================================
-- 2. checkins - 일일 체크인 (핵심 기록)
-- ============================================
CREATE TABLE IF NOT EXISTS checkins (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    content TEXT NOT NULL,  -- 체크인 본문
    mood TEXT CHECK (mood IN ('great', 'good', 'neutral', 'bad', 'terrible')),
    tags TEXT[] DEFAULT '{}',  -- 태그 배열
    metadata JSONB DEFAULT '{}',  -- 추가 메타데이터
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스
CREATE INDEX IF NOT EXISTS idx_checkins_user_id ON checkins(user_id);
CREATE INDEX IF NOT EXISTS idx_checkins_created_at ON checkins(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_checkins_mood ON checkins(mood);
CREATE INDEX IF NOT EXISTS idx_checkins_tags ON checkins USING GIN(tags);

-- ============================================
-- 3. artifacts - 멀티모달 첨부파일
-- ============================================
CREATE TABLE IF NOT EXISTS artifacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    checkin_id UUID REFERENCES checkins(id) ON DELETE CASCADE,
    type TEXT NOT NULL CHECK (type IN ('image', 'audio', 'file')),
    storage_path TEXT NOT NULL,  -- Supabase Storage 경로
    original_name TEXT,
    file_size INTEGER,
    mime_type TEXT,
    metadata JSONB DEFAULT '{}',  -- 분석 결과, 전사 텍스트 등
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스
CREATE INDEX IF NOT EXISTS idx_artifacts_checkin_id ON artifacts(checkin_id);
CREATE INDEX IF NOT EXISTS idx_artifacts_user_id ON artifacts(user_id);

-- ============================================
-- 4. extractions - AI 추출 데이터
-- ============================================
CREATE TABLE IF NOT EXISTS extractions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    source_type TEXT NOT NULL,  -- 'checkin', 'artifact', 'calendar'
    source_id UUID NOT NULL,
    extraction_type TEXT NOT NULL,  -- 'keywords', 'sentiment', 'summary', 'transcription'
    data JSONB NOT NULL,  -- 추출된 데이터
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스
CREATE INDEX IF NOT EXISTS idx_extractions_source ON extractions(source_type, source_id);
CREATE INDEX IF NOT EXISTS idx_extractions_user_id ON extractions(user_id);

-- ============================================
-- 5. calendar_events - 외부 캘린더 동기화
-- ============================================
CREATE TABLE IF NOT EXISTS calendar_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    external_id TEXT,  -- Google Calendar event ID
    provider TEXT DEFAULT 'google',  -- 'google', 'outlook' 등
    title TEXT NOT NULL,
    description TEXT,
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ NOT NULL,
    location TEXT,
    attendees JSONB DEFAULT '[]',
    metadata JSONB DEFAULT '{}',
    synced_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스
CREATE INDEX IF NOT EXISTS idx_calendar_events_user_id ON calendar_events(user_id);
CREATE INDEX IF NOT EXISTS idx_calendar_events_time ON calendar_events(start_time, end_time);
CREATE INDEX IF NOT EXISTS idx_calendar_events_external ON calendar_events(external_id);

-- ============================================
-- 6. plans - 일간 플랜
-- ============================================
CREATE TABLE IF NOT EXISTS plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    plan_date DATE NOT NULL,
    daily_goal TEXT,  -- 오늘의 목표
    notes TEXT,
    reflection TEXT,  -- 하루 마무리 회고
    completion_rate REAL DEFAULT 0,  -- 완료율 (0.0 ~ 1.0)
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, plan_date)
);

-- 인덱스
CREATE INDEX IF NOT EXISTS idx_plans_user_date ON plans(user_id, plan_date);

-- ============================================
-- 7. plan_blocks - 시간 블록
-- ============================================
CREATE TABLE IF NOT EXISTS plan_blocks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    plan_id UUID REFERENCES plans(id) ON DELETE CASCADE,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    title TEXT NOT NULL,
    category TEXT,  -- '업무', '건강', '자기계발', '휴식' 등
    description TEXT,
    is_completed BOOLEAN DEFAULT FALSE,
    is_from_calendar BOOLEAN DEFAULT FALSE,  -- 캘린더에서 동기화된 블록
    calendar_event_id UUID REFERENCES calendar_events(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스
CREATE INDEX IF NOT EXISTS idx_plan_blocks_plan_id ON plan_blocks(plan_id);
CREATE INDEX IF NOT EXISTS idx_plan_blocks_user_id ON plan_blocks(user_id);
CREATE INDEX IF NOT EXISTS idx_plan_blocks_time ON plan_blocks(start_time, end_time);

-- ============================================
-- 8. memory_chunks - RAG용 텍스트 청크
-- ============================================
CREATE TABLE IF NOT EXISTS memory_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    source_type TEXT NOT NULL,  -- 'checkin', 'note', 'calendar', 'extraction'
    source_id UUID NOT NULL,
    content TEXT NOT NULL,
    chunk_index INTEGER DEFAULT 0,  -- 긴 텍스트 분할시 순서
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스
CREATE INDEX IF NOT EXISTS idx_memory_chunks_user_id ON memory_chunks(user_id);
CREATE INDEX IF NOT EXISTS idx_memory_chunks_source ON memory_chunks(source_type, source_id);

-- ============================================
-- 9. memory_embeddings - 벡터 임베딩 (pgvector)
-- ============================================
CREATE TABLE IF NOT EXISTS memory_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    source_type TEXT NOT NULL,
    source_id UUID NOT NULL,
    content TEXT NOT NULL,  -- 원본 텍스트 (검색 결과 표시용)
    embedding vector(1536),  -- OpenAI text-embedding-3-small 차원
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 벡터 인덱스 (코사인 유사도)
CREATE INDEX IF NOT EXISTS idx_memory_embeddings_vector 
ON memory_embeddings USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);

CREATE INDEX IF NOT EXISTS idx_memory_embeddings_user_id ON memory_embeddings(user_id);

-- ============================================
-- RAG 검색 함수 (RPC)
-- ============================================
CREATE OR REPLACE FUNCTION search_memories(
    query_embedding vector(1536),
    match_count INT DEFAULT 5,
    match_threshold FLOAT DEFAULT 0.7,
    user_id_filter TEXT DEFAULT NULL
)
RETURNS TABLE (
    id UUID,
    source_type TEXT,
    source_id UUID,
    content TEXT,
    similarity FLOAT,
    created_at TIMESTAMPTZ
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        me.id,
        me.source_type,
        me.source_id,
        me.content,
        1 - (me.embedding <=> query_embedding) AS similarity,
        me.created_at
    FROM memory_embeddings me
    WHERE 
        (user_id_filter IS NULL OR me.user_id = user_id_filter)
        AND 1 - (me.embedding <=> query_embedding) > match_threshold
    ORDER BY me.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- ============================================
-- RLS (Row Level Security) 정책
-- MVP: 단일 사용자 기준, user_id로 분리
-- ============================================

-- RLS 활성화
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE checkins ENABLE ROW LEVEL SECURITY;
ALTER TABLE artifacts ENABLE ROW LEVEL SECURITY;
ALTER TABLE extractions ENABLE ROW LEVEL SECURITY;
ALTER TABLE calendar_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE plan_blocks ENABLE ROW LEVEL SECURITY;
ALTER TABLE memory_chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE memory_embeddings ENABLE ROW LEVEL SECURITY;

-- MVP용 간단 정책: anon key로 모든 작업 허용 (단일 사용자)
-- 프로덕션에서는 Supabase Auth와 연동하여 auth.uid() 사용

CREATE POLICY "Allow all for anon" ON profiles FOR ALL USING (true);
CREATE POLICY "Allow all for anon" ON checkins FOR ALL USING (true);
CREATE POLICY "Allow all for anon" ON artifacts FOR ALL USING (true);
CREATE POLICY "Allow all for anon" ON extractions FOR ALL USING (true);
CREATE POLICY "Allow all for anon" ON calendar_events FOR ALL USING (true);
CREATE POLICY "Allow all for anon" ON plans FOR ALL USING (true);
CREATE POLICY "Allow all for anon" ON plan_blocks FOR ALL USING (true);
CREATE POLICY "Allow all for anon" ON memory_chunks FOR ALL USING (true);
CREATE POLICY "Allow all for anon" ON memory_embeddings FOR ALL USING (true);

-- ============================================
-- 트리거: updated_at 자동 갱신
-- ============================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_profiles_updated_at
    BEFORE UPDATE ON profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_checkins_updated_at
    BEFORE UPDATE ON checkins
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_plans_updated_at
    BEFORE UPDATE ON plans
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- 초기 데이터 (선택사항)
-- ============================================
-- 기본 프로필 생성
INSERT INTO profiles (user_id, display_name, timezone)
VALUES ('default-user-id', 'User', 'Asia/Seoul')
ON CONFLICT (user_id) DO NOTHING;

