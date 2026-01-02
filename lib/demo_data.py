"""
ReflectOS - 데모 데이터 생성
Settings 페이지에서 테스트용 데이터를 생성/삭제
"""
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import streamlit as st

# 데모 데이터 구분 태그
DEMO_TAG = "__demo__"


# ============================================
# (1) 규칙 기반 Extraction (Checkin.py 로직 복사)
# ============================================

def extract_by_rules(content: str) -> Dict[str, List[str]]:
    """
    규칙 기반으로 텍스트에서 구조화된 정보 추출
    (pages/2_Checkin.py의 로직과 동일)
    
    Args:
        content: 체크인 내용 텍스트
    
    Returns:
        추출된 정보 딕셔너리
    """
    lines = content.strip().split('\n')
    
    tasks = []
    obstacles = []
    projects = []
    insights = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # task: '-' 또는 '•'로 시작하는 줄
        if line.startswith('-') or line.startswith('•') or line.startswith('*'):
            task_text = line.lstrip('-•* ').strip()
            if task_text:
                tasks.append(task_text)
        
        # obstacle: '!' 시작 또는 부정적 키워드 포함
        obstacle_keywords = ['문제', '어려움', '힘들', '막혀', '안됨', '실패', '오류', '버그']
        if line.startswith('!') or any(kw in line for kw in obstacle_keywords):
            obstacle_text = line.lstrip('! ').strip()
            if obstacle_text and obstacle_text not in obstacles:
                obstacles.append(obstacle_text)
        
        # project: '#프로젝트명' 형태
        project_matches = re.findall(r'#(\w+)', line)
        for proj in project_matches:
            if proj not in projects:
                projects.append(proj)
        
        # insight: 인사이트 키워드 포함
        insight_keywords = ['💡', '인사이트', '배움', '깨달음', '발견', '아이디어']
        if any(kw in line for kw in insight_keywords):
            insight_text = line.strip()
            if insight_text and insight_text not in insights:
                insights.append(insight_text)
    
    return {
        "tasks": tasks,
        "obstacles": obstacles,
        "projects": projects,
        "insights": insights,
        "people": [],
        "emotions": []
    }


# ============================================
# (2) 데모 데이터 항목 생성
# ============================================

def build_demo_items(days: int = 7) -> List[Dict]:
    """
    데모용 체크인 항목 생성
    
    Args:
        days: 생성할 일수 (기본 7일)
    
    Returns:
        체크인 항목 리스트 (과거→현재 순)
    """
    # AI 부트캠프 맥락의 데모 콘텐츠
    demo_contents = [
        # Day 0 (가장 오래된)
        """#AIBootcamp 프로젝트 시작!
- 환경 설정 완료 (Python, VSCode)
- Streamlit 기초 학습
- 프로젝트 구조 설계

오류 발생: pip 버전 문제로 패키지 설치 안됨
해결: pip upgrade로 해결

💡 인사이트: 작은 단위로 나눠서 진행하니 덜 막막함""",

        # Day 1
        """#AIBootcamp
- Supabase 연동 작업
- DB 스키마 설계 완료
- 체크인 기능 프로토타입

문제: RLS 정책 설정이 어려움
열심히 문서 읽고 해결함

💡 배움: PostgreSQL RLS는 강력하지만 설정이 까다로움""",

        # Day 2
        """#AIBootcamp #ReflectOS
- OpenAI API 연결 성공
- Extractor 기능 개발
- 테스트 케이스 작성

오류: API 키 형식 문제
힘들었지만 결국 해결!

💡 인사이트: 에러 메시지를 꼼꼼히 읽는게 중요""",

        # Day 3
        """#AIBootcamp
- RAG 기능 구현 시작
- 벡터 임베딩 학습
- pgvector 확장 설정

어려움: 임베딩 차원 매칭 문제
막혔다가 문서에서 답을 찾음

💡 발견: 임베딩 모델마다 차원이 다르다""",

        # Day 4
        """#AIBootcamp #ReflectOS
- 주간 리포트 기능 완성
- UI/UX 개선 작업
- 버그 수정 여러 개

문제: Streamlit session_state 이해 부족
다시 공부해서 해결함""",

        # Day 5
        """#AIBootcamp
- 플래너 기능 개발
- 시간 블록 UI 구현
- 캘린더 연동 준비

실패: Google OAuth 설정 실수
내일 다시 시도 예정

💡 아이디어: 드래그앤드롭으로 블록 이동하면 좋겠다""",

        # Day 6 (오늘/어제)
        """#AIBootcamp #ReflectOS
- 전체 기능 통합 테스트
- 버그 수정 및 최적화
- 문서화 작업 시작

오류: 여러 페이지 간 상태 공유 문제
해결: session_state 구조 개선

💡 인사이트: MVP는 완벽하지 않아도 된다, 핵심만!"""
    ]
    
    moods = ["good", "neutral", "great", "bad", "good", "neutral", "great"]
    
    items = []
    now = datetime.utcnow()
    
    # days개만큼 생성 (과거→현재 순)
    for i in range(min(days, len(demo_contents))):
        # 과거부터 시작 (days-1일 전 ~ 오늘)
        day_offset = days - 1 - i
        target_date = now - timedelta(days=day_offset)
        
        # 시간도 약간씩 다르게 (9시~18시 사이)
        target_date = target_date.replace(
            hour=9 + (i * 2) % 9,
            minute=(i * 13) % 60,
            second=0,
            microsecond=0
        )
        
        items.append({
            "content": demo_contents[i],
            "mood": moods[i % len(moods)],
            "tags": [DEMO_TAG, "AIBootcamp", "demo"],
            "metadata": {
                "is_demo": True,
                "seed_version": 1,
                "day_index": i,
                "energy": 5 + (i % 4)  # 5~8 사이
            },
            "created_at": target_date.isoformat() + "Z"
        })
    
    return items


# ============================================
# (3) 데모 데이터 삭제
# ============================================

def delete_demo_data() -> Dict[str, Any]:
    """
    데모 데이터만 삭제 (tags에 __demo__ 포함된 것)
    
    Returns:
        삭제 결과 딕셔너리
    """
    from lib.config import get_supabase_client, get_current_user_id
    
    result = {
        "deleted_checkins": 0,
        "deleted_extractions": 0,
        "deleted_embeddings": 0,
        "errors": []
    }
    
    try:
        client = get_supabase_client()
        if not client:
            result["errors"].append("Supabase 클라이언트 없음")
            return result
        
        user_id = get_current_user_id()
        
        # 1. 데모 체크인 ID 조회 (tags에 __demo__ 포함)
        demo_checkins = client.table("checkins").select("id").eq(
            "user_id", user_id
        ).contains("tags", [DEMO_TAG]).execute()
        
        demo_ids = [c["id"] for c in (demo_checkins.data or [])]
        
        if not demo_ids:
            return result
        
        # 2. 관련 extractions 삭제
        for checkin_id in demo_ids:
            try:
                client.table("extractions").delete().eq(
                    "source_type", "checkin"
                ).eq("source_id", checkin_id).execute()
                result["deleted_extractions"] += 1
            except Exception as e:
                result["errors"].append(f"extraction 삭제 오류: {e}")
        
        # 3. 관련 memory_embeddings 삭제
        for checkin_id in demo_ids:
            try:
                client.table("memory_embeddings").delete().eq(
                    "source_id", checkin_id
                ).execute()
                result["deleted_embeddings"] += 1
            except Exception as e:
                result["errors"].append(f"embedding 삭제 오류: {e}")
        
        # 4. 관련 memory_chunks 삭제
        for checkin_id in demo_ids:
            try:
                client.table("memory_chunks").delete().eq(
                    "source_id", checkin_id
                ).execute()
            except Exception:
                pass  # memory_chunks는 선택적
        
        # 5. 데모 체크인 삭제
        client.table("checkins").delete().eq(
            "user_id", user_id
        ).contains("tags", [DEMO_TAG]).execute()
        
        result["deleted_checkins"] = len(demo_ids)
        
    except Exception as e:
        result["errors"].append(f"삭제 중 오류: {e}")
    
    return result


# ============================================
# (3) 데모 데이터 시드 (통합 함수)
# ============================================

def seed_demo_data(
    days: int = 7,
    overwrite: bool = False,
    also_index: bool = True
) -> Dict[str, Any]:
    """
    데모 데이터 생성 및 저장
    
    Args:
        days: 생성할 일수
        overwrite: 기존 데모 데이터 삭제 후 재생성
        also_index: RAG 임베딩도 함께 생성
    
    Returns:
        결과 딕셔너리 {deleted_demo_checkins, inserted_checkins, inserted_extractions, indexed, errors}
    """
    from lib.config import get_supabase_client, get_current_user_id
    from lib.supabase_db import insert_checkin, insert_extraction
    from lib.rag import index_checkin, index_extraction
    
    result = {
        "deleted_demo_checkins": 0,
        "inserted_checkins": 0,
        "inserted_extractions": 0,
        "indexed": 0,
        "errors": []
    }
    
    try:
        client = get_supabase_client()
        if not client:
            result["errors"].append("Supabase 클라이언트가 없습니다.")
            return result
        
        user_id = get_current_user_id()
        
        # A) overwrite=True면 기존 데모 데이터 삭제
        if overwrite:
            delete_result = delete_demo_data()
            result["deleted_demo_checkins"] = delete_result.get("deleted_checkins", 0)
            result["errors"].extend(delete_result.get("errors", []))
        
        # B) 데모 항목 생성
        items = build_demo_items(days)
        
        # C) 각 항목 저장
        for item in items:
            try:
                # 1) 체크인 저장
                checkin_data = insert_checkin(
                    content=item["content"],
                    mood=item["mood"],
                    tags=item["tags"],
                    metadata=item["metadata"],
                    created_at=item["created_at"]  # 확장된 인자 사용
                )
                
                if not checkin_data:
                    result["errors"].append(f"체크인 저장 실패: day_index={item['metadata']['day_index']}")
                    continue
                
                result["inserted_checkins"] += 1
                checkin_id = checkin_data.get("id")
                
                # 2) 규칙 기반 추출
                extractions = extract_by_rules(item["content"])
                
                # 3) extraction 저장
                extraction_result = insert_extraction(
                    source_type="checkin",
                    source_id=checkin_id,
                    extraction_type="demo_rule",
                    data=extractions,
                    created_at=item["created_at"]  # 확장된 인자 사용
                )
                
                if extraction_result:
                    result["inserted_extractions"] += 1
                
                # 4) RAG 인덱싱 (also_index=True인 경우)
                if also_index:
                    try:
                        # 체크인 인덱싱
                        if index_checkin(checkin_id, item["content"], extractions):
                            result["indexed"] += 1
                        
                        # extraction 인덱싱
                        index_extraction(checkin_id, "demo_rule", extractions)
                        
                    except Exception as e:
                        result["errors"].append(f"인덱싱 오류: {e}")
                        
            except Exception as e:
                result["errors"].append(f"항목 처리 오류: {e}")
        
    except Exception as e:
        result["errors"].append(f"seed_demo_data 오류: {e}")
    
    return result

