"""
ReflectOS - Report
주간 회고 리포트 생성
Step 7: RAG 기반 주간 분석 + wins/issues/patterns/next_experiments
"""
import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, List, Optional

st.set_page_config(page_title="Report - ReflectOS", page_icon="📊", layout="wide")

st.title("📊 Weekly Report")
st.caption("AI가 생성하는 주간 회고 리포트")

# === 사이드바: 데모 데이터 제외 토글 ===
with st.sidebar:
    exclude_demo = st.checkbox(
        "🧪 데모 데이터 제외",
        value=st.session_state.get("exclude_demo", True)
    )
    st.session_state["exclude_demo"] = exclude_demo


# === 주간 리포트 생성 함수 ===
def generate_weekly_report_json(checkins: List[Dict], extractions: List[Dict]) -> Optional[Dict]:
    """
    주간 데이터를 분석하여 구조화된 리포트 생성
    
    Returns:
        {
            "summary": "한 줄 요약",
            "wins": ["성취1", "성취2", ...],
            "issues": ["문제1", "문제2", ...],
            "patterns": ["패턴1", "패턴2", ...],
            "next_experiments": ["제안1", "제안2", ...],
            "mood_analysis": {"average": "good", "trend": "stable"},
            "stats": {"total_checkins": 7, "total_tasks": 12, ...}
        }
    """
    from lib.openai_client import chat_completion_json
    
    # 체크인 데이터 요약
    checkin_summaries = []
    mood_counts = {"great": 0, "good": 0, "neutral": 0, "bad": 0, "terrible": 0}
    all_tasks = []
    all_obstacles = []
    
    for c in checkins:
        date = c.get("created_at", "")[:10]
        mood = c.get("mood", "neutral")
        content = c.get("content", "")[:300]
        mood_counts[mood] = mood_counts.get(mood, 0) + 1
        checkin_summaries.append(f"[{date}] 기분:{mood}\n{content}")
    
    for e in extractions:
        data = e.get("data", {})
        all_tasks.extend(data.get("tasks", []))
        all_obstacles.extend(data.get("obstacles", []))
    
    combined_text = "\n---\n".join(checkin_summaries)
    
    # JSON 스키마 정의
    report_schema = {
        "type": "object",
        "properties": {
            "summary": {
                "type": "string",
                "description": "이번 주를 한 문장으로 요약"
            },
            "wins": {
                "type": "array",
                "items": {"type": "string"},
                "description": "이번 주 성취/잘한 점 (최대 5개)"
            },
            "issues": {
                "type": "array",
                "items": {"type": "string"},
                "description": "이번 주 어려웠던 점/문제 (최대 5개)"
            },
            "patterns": {
                "type": "array",
                "items": {"type": "string"},
                "description": "발견된 패턴/반복되는 주제 (최대 3개)"
            },
            "next_experiments": {
                "type": "array",
                "items": {"type": "string"},
                "description": "다음 주 시도해볼 것/제안 (최대 3개)"
            }
        },
        "required": ["summary", "wins", "issues", "patterns", "next_experiments"],
        "additionalProperties": False
    }
    
    system_prompt = """당신은 개인 회고 전문가입니다. 
한 주간의 체크인 기록을 분석하여 의미 있는 주간 리포트를 생성합니다.

분석 원칙:
1. 구체적인 성취를 찾아 wins에 기록
2. 반복되는 어려움이나 문제를 issues에 기록
3. 감정/행동/주제의 패턴을 patterns에 기록
4. 실행 가능한 다음 스텝을 next_experiments에 제안

말투: 긍정적이고 지지적으로, 하지만 솔직하게"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"""이번 주 체크인 기록을 분석해주세요:

{combined_text}

추출된 할 일: {', '.join(all_tasks[:10]) if all_tasks else '없음'}
추출된 어려움: {', '.join(all_obstacles[:5]) if all_obstacles else '없음'}
"""}
    ]
    
    result = chat_completion_json(messages, report_schema, temperature=0.7)
    
    if result:
        # 통계 추가
        result["stats"] = {
            "total_checkins": len(checkins),
            "total_tasks": len(all_tasks),
            "total_obstacles": len(all_obstacles),
            "mood_distribution": mood_counts
        }
        
        # 평균 무드 계산
        mood_scores = {"great": 5, "good": 4, "neutral": 3, "bad": 2, "terrible": 1}
        total_score = sum(mood_counts[m] * mood_scores[m] for m in mood_counts)
        total_count = sum(mood_counts.values())
        
        if total_count > 0:
            avg_score = total_score / total_count
            avg_mood = "great" if avg_score >= 4.5 else "good" if avg_score >= 3.5 else "neutral" if avg_score >= 2.5 else "bad" if avg_score >= 1.5 else "terrible"
            result["mood_analysis"] = {
                "average": avg_mood,
                "average_score": round(avg_score, 2)
            }
    
    return result


# === 주간 선택 ===
st.subheader("📅 기간 선택")

# 이번 주 월요일 계산
today = datetime.now().date()
this_monday = today - timedelta(days=today.weekday())
last_monday = this_monday - timedelta(days=7)

# 빠른 선택 버튼 (먼저 배치하여 session_state 수정)
st.caption("빠른 선택:")
bcol1, bcol2, bcol3 = st.columns(3)

# 버튼 상태 체크 (위젯 생성 전에 처리)
this_week_clicked = bcol1.button("이번 주", use_container_width=True, key="btn_this_week")
last_week_clicked = bcol2.button("지난 주", use_container_width=True, key="btn_last_week")
last_2weeks_clicked = bcol3.button("지난 2주", use_container_width=True, key="btn_last_2weeks")

# 버튼에 따라 기본값 결정
if this_week_clicked:
    default_start = this_monday
    default_end = this_monday + timedelta(days=6)
elif last_week_clicked:
    default_start = last_monday
    default_end = last_monday + timedelta(days=6)
elif last_2weeks_clicked:
    default_start = last_monday - timedelta(days=7)
    default_end = last_monday + timedelta(days=6)
else:
    # session_state 또는 기본값 사용
    default_start = st.session_state.get("rpt_start", this_monday)
    default_end = st.session_state.get("rpt_end", this_monday + timedelta(days=6))

col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input(
        "시작일",
        value=default_start,
        help="주의 시작일 (보통 월요일)"
    )
with col2:
    end_date = st.date_input(
        "종료일",
        value=default_end,
        help="주의 종료일 (보통 일요일)"
    )

# 현재 선택된 날짜 저장
st.session_state.rpt_start = start_date
st.session_state.rpt_end = end_date


# === 리포트 생성 ===
if st.button("📝 리포트 생성", use_container_width=True, type="primary"):
    with st.spinner("📊 주간 데이터를 분석 중..."):
        try:
            from lib.supabase_db import get_checkins_date_range
            from lib.config import get_supabase_client, get_current_user_id
            
            client = get_supabase_client()
            user_id = get_current_user_id()
            
            # 체크인 조회
            checkins = get_checkins_date_range(
                start_date=start_date.isoformat(),
                end_date=end_date.isoformat(),
                exclude_demo=st.session_state.get("exclude_demo", True)
            )
            
            if not checkins:
                st.warning(f"⚠️ {start_date} ~ {end_date} 기간에 체크인 기록이 없습니다.")
            else:
                # extractions 조회
                checkin_ids = [c["id"] for c in checkins]
                extractions = []
                
                for cid in checkin_ids:
                    try:
                        ext_response = client.table("extractions").select("*").eq("source_id", cid).execute()
                        if ext_response.data:
                            extractions.extend(ext_response.data)
                    except:
                        pass
                
                # 리포트 생성
                report = generate_weekly_report_json(checkins, extractions)
                
                if report:
                    st.session_state.weekly_report = report
                    st.session_state.report_checkins = checkins
                    st.success("✅ 리포트 생성 완료!")
                else:
                    st.error("리포트 생성에 실패했습니다.")
                    
        except ImportError as e:
            st.error(f"모듈 로드 실패: {e}")
        except Exception as e:
            st.error(f"오류 발생: {e}")


st.divider()

# === 리포트 표시 ===
if st.session_state.get("weekly_report"):
    report = st.session_state.weekly_report
    checkins = st.session_state.get("report_checkins", [])
    
    st.subheader(f"📋 주간 회고 리포트")
    st.caption(f"{start_date} ~ {end_date}")
    
    # 요약
    st.markdown(f"### 💬 한 줄 요약")
    st.info(report.get("summary", ""))
    
    # 통계 카드
    stats = report.get("stats", {})
    mood_analysis = report.get("mood_analysis", {})
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("총 체크인", f"{stats.get('total_checkins', 0)}회")
    with col2:
        st.metric("완료한 일", f"{stats.get('total_tasks', 0)}개")
    with col3:
        mood_emoji = {"great": "😊", "good": "🙂", "neutral": "😐", "bad": "😔", "terrible": "😢"}
        avg_mood = mood_analysis.get("average", "neutral")
        st.metric("평균 기분", mood_emoji.get(avg_mood, "😐"))
    with col4:
        st.metric("어려움", f"{stats.get('total_obstacles', 0)}개")
    
    st.divider()
    
    # 4분면 표시
    col1, col2 = st.columns(2)
    
    with col1:
        # Wins
        with st.container():
            st.markdown("### 🏆 이번 주 성취")
            wins = report.get("wins", [])
            if wins:
                for i, win in enumerate(wins, 1):
                    st.markdown(f"{i}. {win}")
            else:
                st.caption("기록된 성취가 없습니다")
        
        # Patterns
        with st.container():
            st.markdown("### 🔄 발견된 패턴")
            patterns = report.get("patterns", [])
            if patterns:
                for pattern in patterns:
                    st.markdown(f"• {pattern}")
            else:
                st.caption("특별한 패턴이 발견되지 않았습니다")
    
    with col2:
        # Issues
        with st.container():
            st.markdown("### ⚠️ 어려웠던 점")
            issues = report.get("issues", [])
            if issues:
                for i, issue in enumerate(issues, 1):
                    st.markdown(f"{i}. {issue}")
            else:
                st.caption("기록된 어려움이 없습니다")
        
        # Next Experiments
        with st.container():
            st.markdown("### 🚀 다음 주 제안")
            experiments = report.get("next_experiments", [])
            if experiments:
                for exp in experiments:
                    st.checkbox(exp, key=f"exp_{exp[:20]}")
            else:
                st.caption("제안 사항이 없습니다")
    
    # 기분 분포 차트
    st.divider()
    st.markdown("### 📊 기분 분포")
    
    mood_dist = stats.get("mood_distribution", {})
    if any(mood_dist.values()):
        import pandas as pd
        
        mood_data = {
            "기분": ["😊 아주 좋음", "🙂 좋음", "😐 보통", "😔 안 좋음", "😢 매우 안 좋음"],
            "횟수": [
                mood_dist.get("great", 0),
                mood_dist.get("good", 0),
                mood_dist.get("neutral", 0),
                mood_dist.get("bad", 0),
                mood_dist.get("terrible", 0)
            ]
        }
        df = pd.DataFrame(mood_data)
        st.bar_chart(df.set_index("기분"))
    
    # 원문 보기 (소스 링크)
    st.divider()
    with st.expander("📖 원문 체크인 보기"):
        for checkin in checkins:
            with st.container():
                date = checkin.get("created_at", "")[:10]
                mood = checkin.get("mood", "neutral")
                mood_emoji = {"great": "😊", "good": "🙂", "neutral": "😐", "bad": "😔", "terrible": "😢"}
                
                col1, col2 = st.columns([1, 5])
                with col1:
                    st.markdown(f"### {mood_emoji.get(mood, '📝')}")
                    st.caption(date)
                with col2:
                    st.markdown(checkin.get("content", "")[:200] + "...")
                    tags = checkin.get("tags", [])
                    if tags:
                        st.caption(" ".join([f"`{t}`" for t in tags]))

else:
    # 리포트가 없을 때 템플릿 표시
    st.subheader("📋 리포트 미리보기")
    st.caption("위에서 기간을 선택하고 '리포트 생성' 버튼을 클릭하세요")
    
    with st.container():
        st.markdown("""
        ## 주간 회고 리포트 예시
        
        ---
        
        ### 💬 한 줄 요약
        > 업무와 건강의 균형을 찾아가는 한 주였습니다.
        
        ---
        
        ### 🏆 이번 주 성취
        1. 프로젝트 MVP 완료
        2. 아침 명상 5일 연속 달성
        3. 새로운 아이디어 3개 기록
        
        ### ⚠️ 어려웠던 점
        1. 오후 집중력 저하
        2. 회의가 너무 많음
        
        ### 🔄 발견된 패턴
        • 화요일과 목요일에 생산성이 높음
        • 점심 후 에너지 저하
        
        ### 🚀 다음 주 제안
        - [ ] 오후 시간에 산책 추가
        - [ ] 회의 없는 날 만들기
        - [ ] 저녁 회고 습관 시작
        """)
