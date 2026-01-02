"""
ReflectOS - Planner
시간블록 기반 일정 관리
Step 8: AI 기반 시간블록 제안 + 타임라인 표시
"""
import streamlit as st
from datetime import datetime, timedelta, time
from typing import Dict, List, Optional
import json

st.set_page_config(page_title="Planner - ReflectOS", page_icon="📅", layout="wide")

st.title("📅 Time Block Planner")
st.caption("AI가 제안하는 최적의 시간블록 계획")


# === 카테고리 설정 ===
CATEGORIES = {
    "업무": {"icon": "💻", "color": "#74b9ff"},
    "회의": {"icon": "👥", "color": "#a29bfe"},
    "건강": {"icon": "🏃", "color": "#55efc4"},
    "자기계발": {"icon": "📚", "color": "#fdcb6e"},
    "휴식": {"icon": "☕", "color": "#ffeaa7"},
    "생활": {"icon": "🏠", "color": "#fab1a0"},
}


# === AI 시간블록 제안 함수 ===
def generate_time_blocks(
    goals: List[str],
    work_hours: tuple,
    existing_events: List[Dict] = None,
    weekly_insights: str = None
) -> Optional[Dict]:
    """
    AI Planner 에이전트를 사용하여 시간블록 제안
    
    Args:
        goals: 오늘의 목표 (1-2개)
        work_hours: (시작시간, 종료시간) 튜플
        existing_events: 기존 캘린더 이벤트
        weekly_insights: 주간 리포트에서 가져온 인사이트
    
    Returns:
        {
            "time_blocks": [...],
            "daily_goal": "...",
            "tips": [...]
        }
    """
    from lib.openai_client import chat_completion_json
    from lib.prompts import PLANNER_SYSTEM_PROMPT, PLANNER_JSON_SCHEMA
    
    # 기존 이벤트 텍스트로 변환
    events_text = "없음"
    if existing_events:
        events_text = "\n".join([
            f"- {e.get('start_time', '')}~{e.get('end_time', '')}: {e.get('title', '')}"
            for e in existing_events
        ])
    
    # 목표 텍스트
    goals_text = "\n".join([f"- {g}" for g in goals if g])
    
    user_message = f"""
오늘의 목표:
{goals_text}

근무 시간: {work_hours[0]:02d}:00 ~ {work_hours[1]:02d}:00

기존 일정 (피해야 함):
{events_text}

{f'주간 인사이트: {weekly_insights}' if weekly_insights else ''}

위 정보를 바탕으로 오늘 하루 최적의 시간블록 계획을 제안해주세요.
각 블록에 카테고리(업무/회의/건강/자기계발/휴식/생활)를 지정해주세요.
"""

    messages = [
        {"role": "system", "content": PLANNER_SYSTEM_PROMPT},
        {"role": "user", "content": user_message}
    ]
    
    return chat_completion_json(messages, PLANNER_JSON_SCHEMA, temperature=0.7)


# === 타임라인 렌더링 함수 ===
def render_timeline(blocks: List[Dict], start_hour: int = 6, end_hour: int = 23):
    """시간블록을 타임라인으로 렌더링"""
    
    # 블록을 시작 시간 기준으로 정렬
    sorted_blocks = sorted(blocks, key=lambda x: x.get("start_time", "00:00"))
    
    # 시간대별로 블록 매핑
    block_map = {}
    for block in sorted_blocks:
        start = block.get("start_time", "09:00")
        hour = int(start.split(":")[0])
        block_map[hour] = block
    
    # 렌더링
    for hour in range(start_hour, end_hour):
        col1, col2, col3 = st.columns([1, 5, 1])
        
        with col1:
            st.caption(f"{hour:02d}:00")
        
        with col2:
            if hour in block_map:
                block = block_map[hour]
                category = block.get("category", "업무")
                cat_info = CATEGORIES.get(category, {"icon": "📝", "color": "#dfe6e9"})
                
                title = block.get("title", "")
                end_time = block.get("end_time", "")
                priority = block.get("priority", 2)
                priority_stars = "⭐" * priority
                
                st.markdown(
                    f"""<div style="
                        background: {cat_info['color']}; 
                        padding: 12px; 
                        border-radius: 10px;
                        margin: 4px 0;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    ">
                        <strong>{cat_info['icon']} {title}</strong>
                        <br/>
                        <small style="color: #555;">
                            {hour:02d}:00 ~ {end_time} · {category} {priority_stars}
                        </small>
                    </div>""",
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    """<div style="
                        border: 1px dashed #ddd; 
                        padding: 10px; 
                        border-radius: 8px;
                        margin: 4px 0;
                        color: #bbb;
                        text-align: center;
                    ">
                        <small>빈 시간</small>
                    </div>""",
                    unsafe_allow_html=True
                )
        
        with col3:
            if hour in block_map:
                if st.button("✏️", key=f"edit_{hour}"):
                    st.session_state.edit_block = hour


# === 세션 상태 초기화 ===
if "generated_plan" not in st.session_state:
    st.session_state.generated_plan = None
if "plan_date" not in st.session_state:
    st.session_state.plan_date = datetime.now().date()


# === 사이드바: 설정 ===
with st.sidebar:
    st.subheader("⚙️ 플래너 설정")
    
    st.markdown("**근무 시간**")
    col1, col2 = st.columns(2)
    with col1:
        work_start = st.number_input("시작", min_value=5, max_value=12, value=9)
    with col2:
        work_end = st.number_input("종료", min_value=15, max_value=23, value=18)
    
    st.divider()
    
    st.markdown("**에너지 패턴**")
    energy_pattern = st.radio(
        "집중력이 가장 높은 시간대",
        options=["morning", "afternoon", "evening"],
        format_func=lambda x: {
            "morning": "🌅 오전 (9-12시)",
            "afternoon": "☀️ 오후 (13-17시)",
            "evening": "🌙 저녁 (18-21시)"
        }[x],
        horizontal=False
    )
    
    st.divider()
    
    # 주간 리포트 연동
    st.markdown("**주간 리포트 연동**")
    use_weekly = st.checkbox("주간 인사이트 활용", value=True)


# === 메인 영역 ===
col_left, col_right = st.columns([2, 3])

with col_left:
    st.subheader("🎯 오늘의 목표")
    
    # 날짜 선택
    selected_date = st.date_input(
        "📆 날짜",
        value=st.session_state.plan_date
    )
    st.session_state.plan_date = selected_date
    
    st.divider()
    
    # 목표 입력
    goal1 = st.text_input(
        "목표 1 (필수)",
        placeholder="예: API 문서 작성 완료하기",
        key="goal1"
    )
    
    goal2 = st.text_input(
        "목표 2 (선택)",
        placeholder="예: 30분 운동하기",
        key="goal2"
    )
    
    st.divider()
    
    # 기존 일정 표시 (캘린더에서)
    st.markdown("**📅 기존 일정**")
    
    # 캘린더 이벤트 조회 시도
    existing_events = []
    try:
        from lib.config import get_supabase_client, get_current_user_id
        
        client = get_supabase_client()
        user_id = get_current_user_id()
        
        if client:
            # calendar_events에서 해당 날짜 이벤트 조회
            date_str = selected_date.isoformat()
            response = client.table("calendar_events").select("*").eq("user_id", user_id).gte("start_time", f"{date_str}T00:00:00").lte("start_time", f"{date_str}T23:59:59").execute()
            
            if response.data:
                existing_events = response.data
                for event in existing_events:
                    start = event.get("start_time", "")
                    end = event.get("end_time", "")
                    title = event.get("title", "")
                    st.markdown(f"• {start[11:16]}~{end[11:16]}: {title}")
            else:
                st.caption("기존 일정 없음")
    except:
        st.caption("캘린더 연동 필요 (Step 9)")
    
    st.divider()
    
    # AI 계획 생성 버튼
    if st.button("🤖 AI 계획 생성", use_container_width=True, type="primary"):
        if not goal1:
            st.warning("최소 1개의 목표를 입력해주세요!")
        else:
            with st.spinner("🔄 최적의 시간블록을 계획 중..."):
                try:
                    goals = [g for g in [goal1, goal2] if g]
                    
                    # 주간 인사이트 가져오기
                    weekly_insights = None
                    if use_weekly and st.session_state.get("weekly_report"):
                        report = st.session_state.weekly_report
                        patterns = report.get("patterns", [])
                        if patterns:
                            weekly_insights = "패턴: " + ", ".join(patterns[:2])
                    
                    # AI 계획 생성
                    plan = generate_time_blocks(
                        goals=goals,
                        work_hours=(work_start, work_end),
                        existing_events=existing_events,
                        weekly_insights=weekly_insights
                    )
                    
                    if plan:
                        st.session_state.generated_plan = plan
                        st.success("✅ 계획 생성 완료!")
                    else:
                        st.error("계획 생성에 실패했습니다.")
                        
                except ImportError as e:
                    st.error(f"모듈 로드 실패: {e}")
                except Exception as e:
                    st.error(f"오류 발생: {e}")


with col_right:
    st.subheader("⏰ 시간블록 타임라인")
    
    if st.session_state.generated_plan:
        plan = st.session_state.generated_plan
        
        # 일일 목표 표시
        daily_goal = plan.get("daily_goal", "")
        if daily_goal:
            st.info(f"🎯 **오늘의 핵심 목표:** {daily_goal}")
        
        # 타임라인 렌더링
        blocks = plan.get("time_blocks", [])
        if blocks:
            render_timeline(blocks, start_hour=work_start - 1, end_hour=work_end + 2)
        else:
            st.warning("생성된 블록이 없습니다.")
        
        # 팁 표시
        tips = plan.get("tips", [])
        if tips:
            st.divider()
            st.markdown("### 💡 실행 팁")
            for tip in tips:
                st.markdown(f"• {tip}")
        
        # DB 저장 버튼
        st.divider()
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💾 계획 저장", use_container_width=True):
                try:
                    from lib.supabase_db import upsert_plan, insert_plan_block
                    
                    # plans 테이블에 저장
                    plan_data = upsert_plan(
                        plan_date=selected_date.isoformat(),
                        plan_data={
                            "daily_goal": daily_goal,
                            "notes": json.dumps({"tips": tips}, ensure_ascii=False)
                        }
                    )
                    
                    if plan_data:
                        plan_id = plan_data.get("id")
                        
                        # plan_blocks 저장
                        for block in blocks:
                            insert_plan_block(
                                plan_id=plan_id,
                                start_time=block.get("start_time", "09:00"),
                                end_time=block.get("end_time", "10:00"),
                                title=block.get("title", ""),
                                category=block.get("category", "업무")
                            )
                        
                        st.success("✅ 계획이 저장되었습니다!")
                    else:
                        st.error("저장 실패")
                        
                except Exception as e:
                    st.error(f"저장 오류: {e}")
        
        with col2:
            # Step 10: Google Calendar에 이벤트 생성
            try:
                from lib.calendar_google import is_authenticated, create_events_from_plan
                
                calendar_connected = is_authenticated()
                
                if st.button(
                    "📅 캘린더에 반영",
                    use_container_width=True,
                    disabled=not calendar_connected
                ):
                    if not calendar_connected:
                        st.warning("Settings에서 Google Calendar를 연결해주세요.")
                    else:
                        with st.spinner("캘린더에 이벤트 생성 중..."):
                            blocks = plan.get("time_blocks", [])
                            created = create_events_from_plan(
                                plan_date=selected_date.isoformat(),
                                blocks=blocks
                            )
                            
                            if created > 0:
                                st.success(f"✅ {created}개 이벤트가 Google Calendar에 생성되었습니다!")
                            else:
                                st.warning("생성된 이벤트가 없습니다.")
                
                if not calendar_connected:
                    st.caption("💡 Settings에서 Google 연결 필요")
                    
            except ImportError:
                st.button("📅 캘린더에 반영", use_container_width=True, disabled=True)
                st.caption("Google Calendar 모듈 필요")
    
    else:
        # 데모 타임라인
        st.caption("왼쪽에서 목표를 입력하고 'AI 계획 생성'을 클릭하세요")
        
        demo_blocks = [
            {"start_time": "09:00", "end_time": "10:00", "title": "아침 루틴", "category": "건강", "priority": 2},
            {"start_time": "10:00", "end_time": "12:00", "title": "딥워크 - 핵심 업무", "category": "업무", "priority": 3},
            {"start_time": "12:00", "end_time": "13:00", "title": "점심 식사", "category": "휴식", "priority": 1},
            {"start_time": "13:00", "end_time": "15:00", "title": "회의 및 협업", "category": "회의", "priority": 2},
            {"start_time": "15:00", "end_time": "17:00", "title": "오후 업무", "category": "업무", "priority": 2},
            {"start_time": "18:00", "end_time": "19:00", "title": "운동", "category": "건강", "priority": 2},
        ]
        
        render_timeline(demo_blocks, start_hour=8, end_hour=20)


# === 하단: 블록 테이블 뷰 ===
st.divider()
with st.expander("📋 테이블 뷰"):
    if st.session_state.generated_plan:
        blocks = st.session_state.generated_plan.get("time_blocks", [])
        
        if blocks:
            import pandas as pd
            
            df_data = []
            for b in blocks:
                cat = b.get("category", "업무")
                icon = CATEGORIES.get(cat, {}).get("icon", "📝")
                df_data.append({
                    "시작": b.get("start_time", ""),
                    "종료": b.get("end_time", ""),
                    "제목": b.get("title", ""),
                    "카테고리": f"{icon} {cat}",
                    "우선순위": "⭐" * b.get("priority", 1)
                })
            
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.caption("계획을 생성하면 여기에 테이블로 표시됩니다")
