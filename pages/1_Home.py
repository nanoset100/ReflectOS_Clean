"""
ReflectOS - Home (대시보드)
최근 체크인 목록 및 요약 표시
Step 9: Google Calendar 일정 표시
"""
import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Home - ReflectOS", page_icon="🏠", layout="wide")

st.title("🏠 Home")
st.caption("최근 기록과 오늘의 요약을 확인하세요")

# === 사이드바: 데모 데이터 제외 토글 ===
with st.sidebar:
    exclude_demo = st.checkbox(
        "🧪 데모 데이터 제외",
        value=st.session_state.get("exclude_demo", True)
    )
    st.session_state["exclude_demo"] = exclude_demo

# === 오늘의 캘린더 일정 (Step 9) ===
try:
    from lib.calendar_google import is_authenticated, get_today_events
    
    if is_authenticated():
        with st.container():
            st.subheader("📅 오늘 일정")
            
            events = get_today_events()
            if events:
                for event in events[:5]:
                    start = event.get("start_time", "")
                    if "T" in start:
                        start_time = start.split("T")[1][:5]
                    else:
                        start_time = "종일"
                    
                    col1, col2 = st.columns([1, 4])
                    with col1:
                        st.markdown(f"**{start_time}**")
                    with col2:
                        st.markdown(event.get("title", ""))
                
                if len(events) > 5:
                    st.caption(f"외 {len(events) - 5}개 일정...")
            else:
                st.info("오늘 일정이 없습니다 📭")
        
        st.divider()
except:
    pass  # Google Calendar 미연결 시 무시

# === Supabase 연결 상태 체크 ===
try:
    from lib.config import get_supabase_client
    from lib.supabase_db import list_checkins
    
    supabase = get_supabase_client()
    
    if supabase:
        st.success("✅ Supabase 연결됨")
        
        # 최근 체크인 목록 가져오기
        st.subheader("📝 최근 체크인")
        
        checkins = list_checkins(limit=10, exclude_demo=st.session_state.get("exclude_demo", True))
        
        if checkins:
            for checkin in checkins:
                with st.container():
                    # 날짜 포맷팅
                    created_at = checkin.get("created_at", "")
                    if created_at:
                        try:
                            dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                            date_str = dt.strftime("%Y-%m-%d %H:%M")
                        except:
                            date_str = created_at[:16]
                    else:
                        date_str = "날짜 없음"
                    
                    # 무드 이모지 매핑
                    mood_emoji = {
                        "great": "😊",
                        "good": "🙂", 
                        "neutral": "😐",
                        "bad": "😔",
                        "terrible": "😢"
                    }.get(checkin.get("mood", ""), "📝")
                    
                    col1, col2 = st.columns([1, 4])
                    with col1:
                        st.markdown(f"### {mood_emoji}")
                        st.caption(date_str)
                    with col2:
                        st.markdown(checkin.get("content", "*내용 없음*"))
                        
                        # 태그가 있으면 표시
                        tags = checkin.get("tags", [])
                        if tags:
                            st.caption(" ".join([f"`{tag}`" for tag in tags]))
        else:
            st.info("아직 체크인 기록이 없습니다. **Check-in** 페이지에서 첫 기록을 남겨보세요!")
            
    else:
        st.warning("⚠️ Supabase 연결 설정이 필요합니다")
        
except ImportError as e:
    st.warning("⚠️ Supabase 모듈 로드 중... (lib/config.py, lib/supabase_db.py 필요)")
    st.code(str(e))
    
    # 데모 데이터로 UI 미리보기
    st.subheader("📝 최근 체크인 (데모)")
    
    demo_checkins = [
        {"mood": "great", "content": "오늘 프로젝트 MVP 완성! 뿌듯하다.", "date": "2024-01-15 09:30"},
        {"mood": "good", "content": "아침 명상 30분 완료. 집중력이 좋아졌다.", "date": "2024-01-14 08:00"},
        {"mood": "neutral", "content": "회의가 길었지만 나름 생산적이었다.", "date": "2024-01-13 18:00"},
    ]
    
    for item in demo_checkins:
        with st.container():
            mood_emoji = {"great": "😊", "good": "🙂", "neutral": "😐"}.get(item["mood"], "📝")
            col1, col2 = st.columns([1, 4])
            with col1:
                st.markdown(f"### {mood_emoji}")
                st.caption(item["date"])
            with col2:
                st.markdown(item["content"])

except Exception as e:
    st.error(f"오류 발생: {e}")

# === 오늘의 요약 섹션 ===
st.divider()
st.subheader("📊 오늘의 요약")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="체크인", value="0회", delta="목표: 3회")
    
with col2:
    st.metric(label="계획 완료율", value="0%", delta="0/0 블록")
    
with col3:
    st.metric(label="연속 기록", value="0일", delta="최고: 0일")

# === 퀵 액션 ===
st.divider()
st.subheader("⚡ 빠른 시작")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("✍️ 새 체크인", use_container_width=True):
        st.switch_page("pages/2_Checkin.py")
        
with col2:
    if st.button("📅 오늘 플래너", use_container_width=True):
        st.switch_page("pages/4_Planner.py")
        
with col3:
    if st.button("🧠 기억 검색", use_container_width=True):
        st.switch_page("pages/5_Memory.py")

