"""
ReflectOS - 취준생 모듈: 지원 현황 추적
지원한 회사/직무 추적 및 관리
"""
import streamlit as st
from datetime import date
from lib.auth import get_current_user
from lib.supabase_db import create_module_entry, get_module_entries

# 사용자 정보 가져오기
user = get_current_user()
user_id = user.id

st.title("📮 지원 현황")
st.caption("지원한 회사와 직무를 추적하세요")

# 지원 정보 입력 폼
with st.form("application_form", clear_on_submit=True):
    company = st.text_input(
        "회사명",
        placeholder="예: 네이버, 카카오, 삼성전자",
        key="company"
    )
    
    role = st.text_input(
        "직무/포지션",
        placeholder="예: 백엔드 개발자, 프론트엔드 개발자",
        key="role"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        status = st.selectbox(
            "지원 상태",
            options=["지원 완료", "서류 통과", "면접 진행", "최종 합격", "불합격", "포기"],
            index=0,
            key="status"
        )
    with col2:
        applied_on = st.date_input(
            "지원일",
            value=date.today(),
            key="applied_on"
        )
    
    link = st.text_input(
        "지원 링크 (선택)",
        placeholder="https://...",
        key="link"
    )
    
    memo = st.text_area(
        "메모",
        placeholder="특이사항, 준비 내용, 후기 등",
        key="memo"
    )
    
    submit = st.form_submit_button("💾 저장", use_container_width=True, type="primary")
    
    if submit:
        if not company.strip() or not role.strip():
            st.error("❌ 회사명과 직무를 입력해주세요.")
        else:
            try:
                payload = {
                    "company": company,
                    "role": role,
                    "status": status,
                    "applied_on": applied_on.isoformat(),
                    "link": link if link else None,
                    "memo": memo
                }
                
                result = create_module_entry(
                    user_id=user_id,
                    module="jobseeker",
                    entry_type="application",
                    occurred_on=applied_on,
                    payload=payload
                )
                
                if result:
                    st.success("✅ 지원 정보가 저장되었습니다!")
                    st.balloons()
                else:
                    st.error("❌ 저장에 실패했습니다.")
            except Exception as e:
                st.error(f"❌ 오류 발생: {e}")

# 지원 현황 리스트
st.divider()
st.subheader("📊 지원 현황 목록")

# 상태 필터
status_filter = st.selectbox(
    "상태 필터",
    options=["전체", "지원 완료", "서류 통과", "면접 진행", "최종 합격", "불합격", "포기"],
    index=0,
    key="status_filter"
)

try:
    # 모든 지원 정보 조회
    all_applications = get_module_entries(
        user_id=user_id,
        module="jobseeker",
        entry_type="application",
        limit=100
    )
    
    # 상태 필터 적용
    if status_filter != "전체":
        applications = [a for a in all_applications if a.get("payload", {}).get("status") == status_filter]
    else:
        applications = all_applications
    
    # 최신순 정렬
    applications_sorted = sorted(
        applications,
        key=lambda x: x.get("occurred_on", ""),
        reverse=True
    )
    
    if applications_sorted:
        # 상태별 통계
        status_counts = {}
        for app in all_applications:
            status = app.get("payload", {}).get("status", "기타")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # 통계 표시
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("전체 지원", f"{len(all_applications)}건")
        with col2:
            st.metric("서류 통과", f"{status_counts.get('서류 통과', 0)}건")
        with col3:
            st.metric("면접 진행", f"{status_counts.get('면접 진행', 0)}건")
        with col4:
            st.metric("최종 합격", f"{status_counts.get('최종 합격', 0)}건")
        
        st.divider()
        
        # 지원 목록 표시
        for app in applications_sorted:
            occurred_on = app.get("occurred_on", "")
            payload = app.get("payload", {})
            
            company = payload.get("company", "")
            role = payload.get("role", "")
            status = payload.get("status", "")
            link = payload.get("link", "")
            memo = payload.get("memo", "")
            
            # 상태별 색상
            status_colors = {
                "지원 완료": "⚪",
                "서류 통과": "🟡",
                "면접 진행": "🟠",
                "최종 합격": "🟢",
                "불합격": "🔴",
                "포기": "⚫"
            }
            status_icon = status_colors.get(status, "⚪")
            
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 1])
                
                with col1:
                    st.markdown(f"**{company}**")
                    st.caption(f"{role}")
                    st.caption(f"📅 지원일: {occurred_on}")
                
                with col2:
                    st.markdown(f"{status_icon} **{status}**")
                    if link:
                        st.link_button("🔗 지원 링크", link)
                
                with col3:
                    if memo:
                        with st.expander("📝 메모"):
                            st.caption(memo)
                
                st.divider()
    else:
        if status_filter != "전체":
            st.info(f"📭 '{status_filter}' 상태의 지원이 없습니다.")
        else:
            st.info("📭 아직 지원 정보가 없습니다. 위에서 첫 지원을 기록해보세요!")
        
except Exception as e:
    st.error(f"❌ 데이터 조회 중 오류 발생: {e}")
