"""
ReflectOS - RAG (Retrieval Augmented Generation)
벡터 검색 기반 기억 조회 및 컨텍스트 생성
"""
import streamlit as st
from typing import Optional, List, Dict, Any
from datetime import datetime
from lib.config import get_supabase_client, get_current_user_id
from lib.openai_client import create_embedding
from lib.utils import DEMO_TAG


# ============================================
# 임베딩 함수
# ============================================

def embed(text: str) -> Optional[List[float]]:
    """
    텍스트를 벡터 임베딩으로 변환
    
    Args:
        text: 임베딩할 텍스트
    
    Returns:
        1536차원 벡터 (OpenAI text-embedding-3-small)
    """
    return create_embedding(text)


# ============================================
# 메모리 청크 저장
# ============================================

def save_memory_chunk(
    source_type: str,
    source_id: str,
    content: str,
    chunk_index: int = 0,
    metadata: Dict = None,
    user_id: str = None
) -> Optional[Dict]:
    """
    memory_chunks 테이블에 텍스트 조각 저장
    중복 방지: checkin은 단일 유지 정책 적용
    
    Args:
        source_type: 소스 타입 ('checkin', 'extraction', 'calendar', 'plan')
        source_id: 소스 레코드 ID
        content: 텍스트 내용
        chunk_index: 긴 텍스트 분할 시 순서
        metadata: 추가 메타데이터
        user_id: 사용자 ID
    
    Returns:
        저장된 chunk 레코드
    """
    try:
        client = get_supabase_client()
        if not client:
            return None
        
        user_id = user_id or get_current_user_id()
        
        # 중복 방지: checkin인 경우 기존 chunk 확인
        if source_type == "checkin":
            existing = client.table("memory_chunks").select("id, content").eq(
                "user_id", user_id
            ).eq("source_type", source_type).eq("source_id", source_id).eq(
                "chunk_index", chunk_index
            ).execute()
            
            rows = existing.data or []
            if rows:
                # content가 같으면 기존 row 반환 (삽입 X)
                if rows[0].get("content") == content:
                    return rows[0]
                # content가 다르면 삭제 후 새로 삽입
                client.table("memory_chunks").delete().eq(
                    "user_id", user_id
                ).eq("source_type", source_type).eq("source_id", source_id).eq(
                    "chunk_index", chunk_index
                ).execute()
        
        data = {
            "user_id": user_id,
            "source_type": source_type,
            "source_id": source_id,
            "content": content,
            "chunk_index": chunk_index,
            "metadata": metadata or {},
            "created_at": datetime.utcnow().isoformat()
        }
        
        response = client.table("memory_chunks").insert(data).execute()
        return response.data[0] if response.data else None
        
    except Exception as e:
        st.error(f"메모리 청크 저장 실패: {e}")
        return None


def save_memory_embedding(
    source_type: str,
    source_id: str,
    content: str,
    embedding: List[float] = None,
    user_id: str = None
) -> Optional[Dict]:
    """
    memory_embeddings 테이블에 벡터 임베딩 저장
    중복 방지: checkin은 단일 유지, extraction은 동일 content만 스킵
    
    Args:
        source_type: 소스 타입
        source_id: 소스 레코드 ID
        content: 원본 텍스트 (검색 결과 표시용)
        embedding: 벡터 임베딩 (없으면 자동 생성)
        user_id: 사용자 ID
    
    Returns:
        저장된 embedding 레코드
    """
    try:
        client = get_supabase_client()
        if not client:
            return None
        
        user_id = user_id or get_current_user_id()
        
        # 중복 방지: 기존 rows 조회
        existing = client.table("memory_embeddings").select("id, content").eq(
            "user_id", user_id
        ).eq("source_type", source_type).eq("source_id", source_id).execute()
        
        rows = existing.data or []
        
        if source_type == "checkin":
            # checkin: 동일 content면 반환, 다르면 삭제 후 삽입
            for row in rows:
                if row.get("content") == content:
                    return row  # 동일 content, 스킵
            # 기존 것 삭제 (content가 다르거나 새로 삽입)
            if rows:
                client.table("memory_embeddings").delete().eq(
                    "user_id", user_id
                ).eq("source_type", source_type).eq("source_id", source_id).execute()
        else:
            # extraction 등: 동일 content면 스킵, 없으면 삽입 (삭제 X)
            for row in rows:
                if row.get("content") == content:
                    return row  # 동일 content, 스킵
        
        # 임베딩이 없으면 생성
        if embedding is None:
            embedding = embed(content)
            if not embedding:
                return None
        
        data = {
            "user_id": user_id,
            "source_type": source_type,
            "source_id": source_id,
            "content": content,
            "embedding": embedding,
            "created_at": datetime.utcnow().isoformat()
        }
        
        response = client.table("memory_embeddings").insert(data).execute()
        return response.data[0] if response.data else None
        
    except Exception as e:
        st.error(f"임베딩 저장 실패: {e}")
        return None


# ============================================
# 체크인 인덱싱 (통합 함수)
# ============================================

def index_checkin(
    checkin_id: str, 
    content: str,
    extractions: Dict = None
) -> bool:
    """
    체크인 내용을 RAG 인덱스에 추가
    - memory_chunks에 텍스트 저장
    - memory_embeddings에 벡터 저장
    
    Args:
        checkin_id: 체크인 ID
        content: 체크인 내용
        extractions: 추출된 데이터 (tasks, obstacles 등)
    
    Returns:
        성공 여부
    """
    try:
        # 1. memory_chunks에 원본 텍스트 저장
        chunk = save_memory_chunk(
            source_type="checkin",
            source_id=checkin_id,
            content=content,
            metadata={"extractions": extractions} if extractions else {}
        )
        
        # 2. memory_embeddings에 벡터 저장
        embedding_result = save_memory_embedding(
            source_type="checkin",
            source_id=checkin_id,
            content=content
        )
        
        return chunk is not None and embedding_result is not None
        
    except Exception as e:
        st.error(f"체크인 인덱싱 실패: {e}")
        return False


def index_extraction(
    checkin_id: str,
    extraction_type: str,
    data: Dict
) -> bool:
    """
    추출 데이터(tasks, obstacles 등)를 별도 인덱싱
    
    Args:
        checkin_id: 연결된 체크인 ID
        extraction_type: 추출 타입
        data: 추출된 데이터
    
    Returns:
        성공 여부
    """
    try:
        # 추출 데이터를 텍스트로 변환
        text_parts = []
        
        if data.get("tasks"):
            text_parts.append("할 일: " + ", ".join(data["tasks"]))
        if data.get("obstacles"):
            text_parts.append("어려움: " + ", ".join(data["obstacles"]))
        if data.get("projects"):
            text_parts.append("프로젝트: " + ", ".join(data["projects"]))
        if data.get("insights"):
            text_parts.append("인사이트: " + ", ".join(data["insights"]))
        
        if not text_parts:
            return True  # 추출 데이터가 없으면 스킵
        
        content = " | ".join(text_parts)
        
        return save_memory_embedding(
            source_type="extraction",
            source_id=checkin_id,
            content=content
        ) is not None
        
    except Exception as e:
        st.error(f"추출 데이터 인덱싱 실패: {e}")
        return False


# ============================================
# 유사도 검색
# ============================================

def similarity_search(
    query: str,
    top_k: int = 5,
    threshold: float = 0.7,
    source_type_filter: str = None,
    exclude_demo: bool = False
) -> List[Dict]:
    """
    유사 기억 검색 (pgvector 코사인 유사도)
    
    Args:
        query: 검색 쿼리
        top_k: 최대 결과 수
        threshold: 최소 유사도 (0.0 ~ 1.0)
        source_type_filter: 소스 타입 필터 (선택)
        exclude_demo: True면 데모 데이터 기반 결과 제외
    
    Returns:
        유사한 메모리 목록 [{id, source_type, source_id, content, similarity, created_at}]
    """
    try:
        client = get_supabase_client()
        if not client:
            return []
        
        user_id = get_current_user_id()
        
        # 쿼리 임베딩 생성
        query_embedding = embed(query)
        if not query_embedding:
            return []
        
        # pgvector 유사도 검색 (RPC 함수 호출)
        response = client.rpc(
            "search_memories",
            {
                "query_embedding": query_embedding,
                "match_count": top_k,
                "match_threshold": threshold,
                "user_id_filter": user_id
            }
        ).execute()
        
        results = response.data or []
        
        # source_type 필터 적용 (RPC에서 지원 안하면 클라이언트에서)
        if source_type_filter:
            results = [r for r in results if r.get("source_type") == source_type_filter]
        
        # exclude_demo 필터 적용
        if exclude_demo and results:
            # checkin/extraction의 source_id(=checkin_id) 수집
            ids = list({
                r.get("source_id") for r in results 
                if r.get("source_type") in ("checkin", "extraction")
            })
            
            if ids:
                # 해당 checkin들의 tags 조회
                resp = client.table("checkins").select("id, tags").eq(
                    "user_id", user_id
                ).in_("id", ids).execute()
                
                # 데모 태그 포함된 checkin_id 집합
                demo_ids = {
                    row["id"] for row in (resp.data or [])
                    if DEMO_TAG in (row.get("tags") or [])
                }
                
                # 데모 기반 결과 제외
                results = [
                    r for r in results 
                    if not (
                        r.get("source_type") in ("checkin", "extraction") 
                        and r.get("source_id") in demo_ids
                    )
                ]
        
        return results
        
    except Exception as e:
        st.error(f"유사도 검색 실패: {e}")
        return []


# 별칭 (호환성)
search_memories = similarity_search


# ============================================
# 컨텍스트 구성
# ============================================

def build_context(
    memories: List[Dict],
    max_chars: int = 4000,
    include_metadata: bool = True
) -> str:
    """
    검색된 기억을 LLM 컨텍스트 문자열로 구성
    
    Args:
        memories: 검색된 기억 목록
        max_chars: 최대 문자 수
        include_metadata: 날짜/타입 메타데이터 포함 여부
    
    Returns:
        컨텍스트 문자열
    """
    if not memories:
        return "관련 기억이 없습니다."
    
    context_parts = ["[관련 기억]"]
    current_length = 0
    
    for i, memory in enumerate(memories, 1):
        content = memory.get("content", "")
        source_type = memory.get("source_type", "unknown")
        created_at = str(memory.get("created_at", ""))[:10]  # 날짜만
        similarity = memory.get("similarity", 0)
        
        if include_metadata:
            entry = f"\n{i}. [{created_at}] ({source_type}, 유사도: {similarity:.2f})\n   {content}"
        else:
            entry = f"\n{i}. {content}"
        
        if current_length + len(entry) > max_chars:
            context_parts.append("\n... (더 많은 기억이 있음)")
            break
        
        context_parts.append(entry)
        current_length += len(entry)
    
    return "".join(context_parts)


def get_sources_info(memories: List[Dict]) -> List[Dict]:
    """
    검색 결과에서 소스 정보 추출 (출처 표시용)
    
    Args:
        memories: 검색된 기억 목록
    
    Returns:
        소스 정보 목록 [{source_type, source_id, date, preview}]
    """
    sources = []
    
    for memory in memories:
        sources.append({
            "source_type": memory.get("source_type", "unknown"),
            "source_id": memory.get("source_id"),
            "date": str(memory.get("created_at", ""))[:10],
            "preview": memory.get("content", "")[:100] + "...",
            "similarity": memory.get("similarity", 0)
        })
    
    return sources


# ============================================
# RAG 기반 답변 생성
# ============================================

def generate_rag_answer(
    query: str,
    top_k: int = 5,
    threshold: float = 0.6,
    exclude_demo: bool = False
) -> Dict[str, Any]:
    """
    RAG 파이프라인: 검색 → 컨텍스트 구성 → 답변 생성
    
    Args:
        query: 사용자 질문
        top_k: 검색 결과 수
        threshold: 유사도 임계값
        exclude_demo: True면 데모 데이터 기반 결과 제외
    
    Returns:
        {
            "answer": "AI 답변",
            "sources": [...소스 정보...],
            "context": "사용된 컨텍스트"
        }
    """
    from lib.openai_client import chat_completion
    from lib.prompts import RAG_INSIGHT_PROMPT
    
    # 1. 유사 기억 검색
    memories = similarity_search(query, top_k=top_k, threshold=threshold, exclude_demo=exclude_demo)
    
    # 2. 컨텍스트 구성
    context = build_context(memories)
    sources = get_sources_info(memories)
    
    # 3. 답변 생성
    if not memories:
        answer = "관련된 기억을 찾지 못했습니다. 더 많은 체크인을 기록하면 더 좋은 답변을 드릴 수 있어요!"
    else:
        messages = [
            {"role": "system", "content": RAG_INSIGHT_PROMPT},
            {"role": "user", "content": f"질문: {query}\n\n{context}"}
        ]
        
        answer = chat_completion(messages, temperature=0.7, max_tokens=800)
        
        if not answer:
            answer = "답변 생성에 실패했습니다. 다시 시도해주세요."
    
    return {
        "answer": answer,
        "sources": sources,
        "context": context,
        "memories_count": len(memories)
    }


# 별칭 (기존 호환성)
def generate_insight(query: str, context: str) -> Optional[str]:
    """컨텍스트 기반 인사이트 생성 (기존 호환성)"""
    from lib.openai_client import chat_completion
    from lib.prompts import RAG_INSIGHT_PROMPT
    
    messages = [
        {"role": "system", "content": RAG_INSIGHT_PROMPT},
        {"role": "user", "content": f"질문: {query}\n\n{context}"}
    ]
    
    return chat_completion(messages, temperature=0.7)
