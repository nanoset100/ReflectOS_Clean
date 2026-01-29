"""
ReflectOS - 취준생 모듈: 이력서 관리
이력서 버전 관리 및 기록
"""
import streamlit as st
from datetime import date
from lib.auth import get_current_user
from lib.supabase_db import create_module_entry, get_module_entries

# 사용자 정보 가져오기
user = get_current_user()
user_id = user.id

st.title("📄 이력서 관리")
st.caption("이력서 버전을 관리하고 기록하세요")

# 이력서 입력 폼
with st.form("resume_form", clear_on_submit=True):
    title = st.text_input(
        "이력서 제목",
        placeholder="예: 백엔드 개발자 이력서, 프론트엔드 포트폴리오",
        key="title"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        version = st.text_input(
            "버전",
            placeholder="예: v1.0, v2.1, 2024-01",
            key="version"
        )
    with col2:
        created_date = st.date_input(
            "작성일",
            value=date.today(),
            key="created_date"
        )
    
    content = st.text_area(
        "이력서 내용 요약",
        placeholder="주요 내용, 변경 사항, 강조 포인트 등을 간단히 기록",
        height=150,
        key="content"
    )
    
    memo = st.text_area(
        "메모",
        placeholder="특이사항, 피드백, 개선 계획 등",
        key="memo"
    )
    
    submit = st.form_submit_button("💾 저장", use_container_width=True, type="primary")
    
    if submit:
        if not title.strip():
            st.error("❌ 이력서 제목을 입력해주세요.")
        else:
            try:
                payload = {
                    "title": title,
                    "version": version if version else None,
                    "content": content,
                    "memo": memo,
                    "created_date": created_date.isoformat()
                }
                
                result = create_module_entry(
                    user_id=user_id,
                    module="jobseeker",
                    entry_type="resume",
                    occurred_on=created_date,
                    payload=payload
                )
                
                if result:
                    st.success("✅ 이력서가 저장되었습니다!")
                    st.balloons()
                else:
                    st.error("❌ 저장에 실패했습니다.")
            except Exception as e:
                st.error(f"❌ 오류 발생: {e}")

# 이력서 목록 (최신순)
st.divider()
st.subheader("📚 이력서 목록")

try:
    resumes = get_module_entries(
        user_id=user_id,
        module="jobseeker",
        entry_type="resume",
        limit=50
    )
    
    if resumes:
        # 최신순 정렬
        resumes_sorted = sorted(
            resumes,
            key=lambda x: x.get("created_at", ""),
            reverse=True
        )
        
        for resume in resumes_sorted:
            created_at = resume.get("created_at", "")[:10]
            payload = resume.get("payload", {})
            
            title = payload.get("title", "")
            version = payload.get("version", "")
            content = payload.get("content", "")
            memo = payload.get("memo", "")
            created_date = payload.get("created_date", "")
            
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    if version:
                        st.markdown(f"**{title}** (v{version})")
                    else:
                        st.markdown(f"**{title}**")
                    
                    st.caption(f"📅 작성일: {created_date or created_at}")
                    
                    if content:
                        with st.expander("📝 내용 요약"):
                            st.caption(content)
                    
                    if memo:
                        with st.expander("💭 메모"):
                            st.caption(memo)
                
                with col2:
                    st.caption(f"저장: {created_at}")
                
                st.divider()
    else:
        st.info("📭 아직 이력서 기록이 없습니다. 위에서 첫 이력서를 기록해보세요!")
        
except Exception as e:
    st.error(f"❌ 데이터 조회 중 오류 발생: {e}")
