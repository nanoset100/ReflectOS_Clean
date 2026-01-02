"""
ReflectOS - Memory
RAG 기반 기억 검색 및 인사이트 생성
Step 6: 벡터 검색 + 소스 표시
"""
import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Memory - ReflectOS", page_icon="🧠", layout="wide")

st.title("🧠 Memory Search")
st.caption("AI가 과거 기록에서 관련 내용을 찾아 답변합니다")

# === 사이드바: 검색 설정 ===
with st.sidebar:
    st.subheader("⚙️ 검색 설정")
    
    top_k = st.slider(
        "검색 결과 수",
        min_value=3,
        max_value=10,
        value=5,
        help="유사한 기억을 몇 개까지 찾을지"
    )
    
    threshold = st.slider(
        "유사도 임계값",
        min_value=0.3,
        max_value=0.9,
        value=0.6,
        step=0.1,
        help="이 값 이상의 유사도만 표시"
    )
    
    show_context = st.checkbox(
        "컨텍스트 표시",
        value=False,
        help="AI가 참조한 전체 컨텍스트 표시"
    )
    
    st.divider()
    
    exclude_demo = st.checkbox(
        "🧪 데모 데이터 제외",
        value=st.session_state.get("exclude_demo", True)
    )
    st.session_state["exclude_demo"] = exclude_demo
    
    st.divider()
    st.caption("💡 더 많은 체크인을 기록할수록\n검색 정확도가 높아집니다")


# === 검색 입력 ===
st.subheader("🔍 무엇이 궁금하세요?")

search_query = st.text_input(
    "질문 입력",
    placeholder="예: 내가 자주 미루는 이유는? / 지난달 성취한 것들 / 건강 관련 기록...",
    label_visibility="collapsed"
)

col1, col2 = st.columns([3, 1])
with col1:
    search_btn = st.button("🔎 검색하기", use_container_width=True, type="primary")
with col2:
    example_btn = st.button("💡 예시 질문", use_container_width=True)

# 예시 질문 선택
if example_btn:
    st.session_state.show_examples = True

if st.session_state.get("show_examples"):
    example_questions = [
        "내가 자주 미루는 이유가 뭘까?",
        "최근 한 달간 기분 패턴은?",
        "내가 언급한 프로젝트들은?",
        "스트레스 받을 때 뭘 했지?",
        "성공적이었던 습관들은?"
    ]
    
    selected = st.selectbox(
        "예시 질문 선택",
        options=["선택하세요..."] + example_questions,
        label_visibility="collapsed"
    )
    
    if selected != "선택하세요...":
        search_query = selected
        st.session_state.show_examples = False
        st.rerun()


# === 검색 실행 ===
if search_btn and search_query:
    with st.spinner("🔄 기억을 검색하고 답변을 생성 중..."):
        try:
            from lib.rag import generate_rag_answer, similarity_search, get_sources_info
            
            # RAG 파이프라인 실행
            result = generate_rag_answer(
                query=search_query,
                top_k=top_k,
                threshold=threshold,
                exclude_demo=st.session_state.get("exclude_demo", True)
            )
            
            # === 답변 표시 ===
            st.divider()
            st.subheader("💬 AI 답변")
            
            st.markdown(result["answer"])
            
            # === 소스(출처) 표시 ===
            if result["sources"]:
                st.divider()
                st.subheader(f"📚 참조한 기억 ({result['memories_count']}개)")
                
                for i, source in enumerate(result["sources"], 1):
                    with st.container():
                        col1, col2, col3 = st.columns([1, 4, 1])
                        
                        with col1:
                            # 소스 타입 아이콘
                            type_icons = {
                                "checkin": "✍️",
                                "extraction": "📋",
                                "calendar": "📅",
                                "plan": "📝"
                            }
                            icon = type_icons.get(source["source_type"], "📄")
                            st.markdown(f"### {icon}")
                            st.caption(source["date"])
                        
                        with col2:
                            st.markdown(f"**{source['source_type'].upper()}**")
                            st.markdown(source["preview"])
                        
                        with col3:
                            similarity_pct = source["similarity"] * 100
                            st.metric("유사도", f"{similarity_pct:.0f}%")
                        
                        # 원문 보기 버튼
                        if st.button(f"📖 원문 보기", key=f"view_source_{i}"):
                            st.session_state[f"show_full_{i}"] = True
                        
                        if st.session_state.get(f"show_full_{i}"):
                            # 전체 내용 조회 (체크인인 경우)
                            if source["source_type"] == "checkin":
                                try:
                                    from lib.supabase_db import get_checkin
                                    checkin = get_checkin(source["source_id"])
                                    if checkin:
                                        with st.expander("전체 내용", expanded=True):
                                            st.markdown(checkin.get("content", ""))
                                            st.caption(f"기분: {checkin.get('mood', '-')} | 태그: {', '.join(checkin.get('tags', []))}")
                                except:
                                    pass
            
            # === 컨텍스트 표시 (선택적) ===
            if show_context and result.get("context"):
                with st.expander("🔍 AI가 참조한 컨텍스트"):
                    st.code(result["context"], language=None)
            
        except ImportError as e:
            st.error(f"모듈 로드 실패: {e}")
            st.info("lib/rag.py, lib/openai_client.py가 필요합니다.")
        except Exception as e:
            st.error(f"검색 중 오류 발생: {e}")


st.divider()

# === 기억 통계 및 관리 ===
st.subheader("📊 기억 저장소 현황")

try:
    from lib.config import get_supabase_client, get_current_user_id
    
    client = get_supabase_client()
    user_id = get_current_user_id()
    
    if client:
        # 통계 조회
        checkins_count = client.table("checkins").select("id", count="exact").eq("user_id", user_id).execute()
        embeddings_count = client.table("memory_embeddings").select("id", count="exact").eq("user_id", user_id).execute()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("총 체크인", f"{checkins_count.count or 0}개")
        with col2:
            st.metric("벡터 임베딩", f"{embeddings_count.count or 0}개")
        with col3:
            # 인덱싱 비율
            if checkins_count.count and checkins_count.count > 0:
                ratio = (embeddings_count.count or 0) / checkins_count.count * 100
                st.metric("인덱싱 비율", f"{ratio:.0f}%")
            else:
                st.metric("인덱싱 비율", "-")
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("총 체크인", "?")
        with col2:
            st.metric("벡터 임베딩", "?")
        with col3:
            st.metric("인덱싱 비율", "-")
        st.warning("Supabase 연결이 필요합니다.")
        
except Exception as e:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("총 체크인", "?")
    with col2:
        st.metric("벡터 임베딩", "?")
    with col3:
        st.metric("인덱싱 비율", "-")


# === 수동 동기화 ===
st.divider()
st.subheader("🔄 기억 동기화")
st.caption("아직 인덱싱되지 않은 체크인을 벡터로 변환합니다")

if st.button("📥 체크인 동기화", use_container_width=True):
    with st.spinner("동기화 중..."):
        try:
            from lib.config import get_supabase_client, get_current_user_id
            from lib.rag import index_checkin
            
            client = get_supabase_client()
            user_id = get_current_user_id()
            
            if not client:
                st.error("Supabase 연결 실패")
            else:
                # 아직 인덱싱되지 않은 체크인 조회
                # (간단히: 모든 체크인 가져와서 기존 임베딩과 비교)
                checkins = client.table("checkins").select("id, content").eq("user_id", user_id).execute()
                existing = client.table("memory_embeddings").select("source_id").eq("user_id", user_id).eq("source_type", "checkin").execute()
                
                existing_ids = {e["source_id"] for e in (existing.data or [])}
                new_checkins = [c for c in (checkins.data or []) if c["id"] not in existing_ids]
                
                if not new_checkins:
                    st.info("✅ 모든 체크인이 이미 동기화되어 있습니다.")
                else:
                    progress = st.progress(0)
                    success_count = 0
                    
                    for i, checkin in enumerate(new_checkins):
                        if index_checkin(checkin["id"], checkin["content"]):
                            success_count += 1
                        progress.progress((i + 1) / len(new_checkins))
                    
                    st.success(f"✅ {success_count}/{len(new_checkins)}개 체크인 동기화 완료!")
                    st.rerun()
                    
        except Exception as e:
            st.error(f"동기화 실패: {e}")
