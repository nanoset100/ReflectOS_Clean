"""
ReflectOS - 유틸리티 함수
공통으로 사용되는 헬퍼 함수 모음
"""
from datetime import datetime, timedelta
from typing import List, Optional
import re
import matplotlib.pyplot as plt
import matplotlib
import platform

# 데모 데이터 구분 태그 상수
DEMO_TAG = "__demo__"


def setup_korean_font():
    """Matplotlib에서 한글 폰트를 설정합니다.
    서버 환경에서도 동작하도록 여러 폰트 후보를 시도합니다.
    """
    # 한글 폰트 후보 리스트
    font_candidates = [
        "Noto Sans CJK KR",
        "NanumGothic",
        "Malgun Gothic",
        "DejaVu Sans"
    ]
    
    # 시스템에 설치된 폰트 목록 확인
    available_fonts = set(f.name for f in matplotlib.font_manager.fontManager.ttflist)
    
    # 사용 가능한 첫 번째 폰트 선택
    font_name = None
    for candidate in font_candidates:
        if candidate in available_fonts:
            font_name = candidate
            break
    
    # 폰트가 없으면 기본값 사용
    if font_name is None:
        font_name = "DejaVu Sans"
    
    # matplotlib 폰트 설정
    plt.rcParams['font.family'] = font_name
    
    # 음수 기호 설정 (마이너스 기호 유니코드 문제 해결)
    plt.rcParams['axes.unicode_minus'] = False


def has_demo_tag(tags):
    """tags 배열에 DEMO_TAG가 포함되어 있는지 확인 (None/빈배열 안전)"""
    return bool(tags) and (DEMO_TAG in tags)


def format_datetime(dt_string: str, format: str = "%Y-%m-%d %H:%M") -> str:
    """ISO datetime 문자열을 포맷팅"""
    try:
        dt = datetime.fromisoformat(dt_string.replace("Z", "+00:00"))
        return dt.strftime(format)
    except:
        return dt_string[:16] if dt_string else ""


def get_week_range(date: datetime = None) -> tuple:
    """주어진 날짜가 속한 주의 시작/종료일 반환"""
    if date is None:
        date = datetime.now()
    
    # 월요일 시작
    start = date - timedelta(days=date.weekday())
    end = start + timedelta(days=6)
    
    return (start.date(), end.date())


def parse_tags(tags_string: str) -> List[str]:
    """쉼표로 구분된 태그 문자열을 리스트로 변환"""
    if not tags_string:
        return []
    return [tag.strip() for tag in tags_string.split(",") if tag.strip()]


def tags_to_string(tags: List[str]) -> str:
    """태그 리스트를 쉼표 구분 문자열로 변환"""
    return ", ".join(tags) if tags else ""


def estimate_tokens(text: str) -> int:
    """텍스트의 토큰 수 대략적 추정 (한국어/영어 혼합 기준)"""
    # 한글은 약 1.5토큰/글자, 영어는 약 0.25토큰/단어
    korean_chars = len(re.findall(r'[가-힣]', text))
    english_words = len(re.findall(r'[a-zA-Z]+', text))
    
    return int(korean_chars * 1.5 + english_words * 1.3 + len(text) * 0.1)


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """텍스트를 지정 길이로 자르기"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def mood_to_emoji(mood: str) -> str:
    """무드 문자열을 이모지로 변환"""
    return {
        "great": "😊",
        "good": "🙂",
        "neutral": "😐",
        "bad": "😔",
        "terrible": "😢"
    }.get(mood, "📝")


def mood_to_score(mood: str) -> int:
    """무드를 점수로 변환 (1-5)"""
    return {
        "terrible": 1,
        "bad": 2,
        "neutral": 3,
        "good": 4,
        "great": 5
    }.get(mood, 3)


def calculate_streak(dates: List[datetime]) -> int:
    """연속 기록 일수 계산"""
    if not dates:
        return 0
    
    # 날짜 정렬 (최신순)
    sorted_dates = sorted(set(d.date() for d in dates), reverse=True)
    
    if sorted_dates[0] != datetime.now().date():
        return 0
    
    streak = 1
    for i in range(len(sorted_dates) - 1):
        if (sorted_dates[i] - sorted_dates[i + 1]).days == 1:
            streak += 1
        else:
            break
    
    return streak


def time_ago(dt_string: str) -> str:
    """상대적 시간 표시 (예: '3시간 전')"""
    try:
        dt = datetime.fromisoformat(dt_string.replace("Z", "+00:00"))
        now = datetime.now(dt.tzinfo)
        diff = now - dt
        
        if diff.days > 7:
            return dt.strftime("%Y-%m-%d")
        elif diff.days > 0:
            return f"{diff.days}일 전"
        elif diff.seconds > 3600:
            return f"{diff.seconds // 3600}시간 전"
        elif diff.seconds > 60:
            return f"{diff.seconds // 60}분 전"
        else:
            return "방금 전"
    except:
        return ""

