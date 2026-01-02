"""
ReflectOS - OpenAI 클라이언트
GPT, Embeddings, Whisper(STT), Structured Outputs 통합
"""
import json
import streamlit as st
from openai import OpenAI
from lib.config import get_openai_api_key
from typing import Optional, List, Dict, Any


@st.cache_resource
def get_openai_client() -> Optional[OpenAI]:
    """OpenAI 클라이언트 싱글톤"""
    api_key = get_openai_api_key()
    if not api_key:
        return None
    return OpenAI(api_key=api_key)


def chat_completion(
    messages: List[dict],
    model: str = "gpt-4o-mini",
    temperature: float = 0.7,
    max_tokens: int = 1000
) -> Optional[str]:
    """
    ChatGPT 응답 생성
    
    Args:
        messages: [{"role": "system/user/assistant", "content": "..."}]
        model: 모델명
        temperature: 창의성 (0.0 ~ 1.0)
        max_tokens: 최대 토큰 수
    
    Returns:
        응답 텍스트
    """
    try:
        client = get_openai_client()
        if not client:
            st.warning("OpenAI API 키가 설정되지 않았습니다.")
            return None
        
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        st.error(f"ChatGPT 호출 실패: {e}")
        return None


def chat_completion_json(
    messages: List[dict],
    json_schema: Dict[str, Any],
    model: str = "gpt-4o-mini",
    temperature: float = 0.3
) -> Optional[Dict]:
    """
    Structured Outputs를 사용한 JSON 응답 생성
    
    Args:
        messages: 대화 메시지 리스트
        json_schema: JSON Schema 정의 (response_format에 사용)
        model: 모델명 (gpt-4o-mini 권장)
        temperature: 낮은 값 권장 (구조화된 출력용)
    
    Returns:
        파싱된 JSON 딕셔너리
    """
    try:
        client = get_openai_client()
        if not client:
            st.warning("OpenAI API 키가 설정되지 않았습니다.")
            return None
        
        # Structured Outputs 사용 (response_format)
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "extraction_result",
                    "strict": True,
                    "schema": json_schema
                }
            }
        )
        
        content = response.choices[0].message.content
        return json.loads(content)
        
    except json.JSONDecodeError as e:
        st.error(f"JSON 파싱 실패: {e}")
        return None
    except Exception as e:
        st.error(f"Structured Output 호출 실패: {e}")
        return None


def ingest_text(raw_text: str) -> Optional[str]:
    """
    Ingestor: 원본 텍스트를 정리/정규화
    
    Args:
        raw_text: 사용자가 입력한 원본 텍스트
    
    Returns:
        정리된 clean_text
    """
    from lib.prompts import INGESTOR_SYSTEM_PROMPT
    
    messages = [
        {"role": "system", "content": INGESTOR_SYSTEM_PROMPT},
        {"role": "user", "content": raw_text}
    ]
    
    return chat_completion(messages, temperature=0.3, max_tokens=2000)


def extract_structured_data(text: str) -> Optional[Dict]:
    """
    Extractor: 텍스트에서 구조화된 정보 추출 (Structured Outputs)
    
    Args:
        text: 분석할 텍스트 (정리된 clean_text 권장)
    
    Returns:
        추출된 데이터 딕셔너리:
        {
            "tasks": [...],
            "obstacles": [...],
            "projects": [...],
            "insights": [...],
            "people": [...],
            "emotions": [...]
        }
    """
    from lib.prompts import EXTRACTOR_SYSTEM_PROMPT, EXTRACTOR_JSON_SCHEMA
    
    messages = [
        {"role": "system", "content": EXTRACTOR_SYSTEM_PROMPT},
        {"role": "user", "content": f"다음 체크인에서 정보를 추출해주세요:\n\n{text}"}
    ]
    
    return chat_completion_json(messages, EXTRACTOR_JSON_SCHEMA, temperature=0.2)


def generate_reflection(
    checkin_text: str,
    context: str = None,
    style: str = "supportive"
) -> Optional[str]:
    """
    Reflector: 회고 및 인사이트 생성
    
    Args:
        checkin_text: 현재 체크인 텍스트
        context: 과거 기록 컨텍스트 (RAG 결과)
        style: 응답 스타일 ('supportive', 'analytical', 'motivational')
    
    Returns:
        회고 텍스트
    """
    from lib.prompts import REFLECTOR_SYSTEM_PROMPT
    
    user_message = f"체크인 내용:\n{checkin_text}"
    
    if context:
        user_message += f"\n\n관련 과거 기록:\n{context}"
    
    messages = [
        {"role": "system", "content": REFLECTOR_SYSTEM_PROMPT},
        {"role": "user", "content": user_message}
    ]
    
    return chat_completion(messages, temperature=0.7, max_tokens=500)


def generate_weekly_report(checkins: List[Dict]) -> Optional[str]:
    """
    주간 리포트 생성
    
    Args:
        checkins: 한 주간의 체크인 레코드 리스트
    
    Returns:
        주간 리포트 텍스트
    """
    from lib.prompts import WEEKLY_REFLECTOR_PROMPT
    
    # 체크인 요약 텍스트 생성
    checkin_summary = []
    for c in checkins:
        date = c.get("created_at", "")[:10]
        mood = c.get("mood", "")
        content = c.get("content", "")[:200]  # 200자 제한
        checkin_summary.append(f"[{date}] 기분:{mood}\n{content}")
    
    combined_text = "\n---\n".join(checkin_summary)
    
    messages = [
        {"role": "system", "content": WEEKLY_REFLECTOR_PROMPT},
        {"role": "user", "content": f"이번 주 체크인 기록:\n\n{combined_text}"}
    ]
    
    return chat_completion(messages, temperature=0.7, max_tokens=1000)


def suggest_time_blocks(
    tasks: List[str],
    available_hours: int = 8,
    energy_pattern: str = "morning"
) -> Optional[Dict]:
    """
    Planner: 시간 블록 제안
    
    Args:
        tasks: 할 일 목록
        available_hours: 사용 가능한 시간
        energy_pattern: 에너지 패턴 ('morning', 'afternoon', 'evening')
    
    Returns:
        시간 블록 제안 딕셔너리
    """
    from lib.prompts import PLANNER_SYSTEM_PROMPT, PLANNER_JSON_SCHEMA
    
    task_list = "\n".join([f"- {t}" for t in tasks])
    
    messages = [
        {"role": "system", "content": PLANNER_SYSTEM_PROMPT},
        {"role": "user", "content": f"""
오늘 할 일:
{task_list}

사용 가능 시간: {available_hours}시간
에너지 패턴: {energy_pattern} (이 시간대에 집중력이 높음)

최적의 시간 블록을 제안해주세요.
"""}
    ]
    
    return chat_completion_json(messages, PLANNER_JSON_SCHEMA, temperature=0.5)


def create_embedding(text: str, model: str = "text-embedding-3-small") -> Optional[List[float]]:
    """
    텍스트 임베딩 생성 (RAG용)
    
    Args:
        text: 임베딩할 텍스트
        model: 임베딩 모델
    
    Returns:
        벡터 (float 리스트)
    """
    try:
        client = get_openai_client()
        if not client:
            return None
        
        response = client.embeddings.create(
            model=model,
            input=text
        )
        
        return response.data[0].embedding
        
    except Exception as e:
        st.error(f"임베딩 생성 실패: {e}")
        return None


def transcribe_audio(
    audio_file,
    language: str = "ko"
) -> Optional[str]:
    """
    음성을 텍스트로 변환 (Whisper)
    
    Args:
        audio_file: 오디오 파일 객체 (file-like object)
        language: 언어 코드
    
    Returns:
        변환된 텍스트
    """
    try:
        client = get_openai_client()
        if not client:
            return None
        
        response = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language=language
        )
        
        return response.text
        
    except Exception as e:
        st.error(f"음성 변환 실패: {e}")
        return None


def analyze_image(
    image_url: str,
    prompt: str = "이 이미지를 설명해주세요."
) -> Optional[str]:
    """
    이미지 분석 (GPT-4 Vision)
    
    Args:
        image_url: 이미지 URL
        prompt: 분석 프롬프트
    
    Returns:
        분석 결과 텍스트
    """
    try:
        client = get_openai_client()
        if not client:
            return None
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ]
                }
            ],
            max_tokens=500
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        st.error(f"이미지 분석 실패: {e}")
        return None


# === 편의 함수: 체크인 전체 처리 파이프라인 ===

def process_checkin_with_ai(raw_content: str, use_ingestor: bool = True) -> Dict[str, Any]:
    """
    체크인 텍스트 전체 AI 처리 파이프라인
    
    Args:
        raw_content: 사용자 입력 원본 텍스트
        use_ingestor: Ingestor로 정리할지 여부
    
    Returns:
        {
            "clean_text": "정리된 텍스트",
            "extractions": {...추출된 데이터...},
            "reflection": "간단한 코멘트"
        }
    """
    result = {
        "clean_text": raw_content,
        "extractions": None,
        "reflection": None
    }
    
    # Step 1: Ingestor (선택적)
    if use_ingestor:
        clean_text = ingest_text(raw_content)
        if clean_text:
            result["clean_text"] = clean_text
    
    # Step 2: Extractor
    extractions = extract_structured_data(result["clean_text"])
    if extractions:
        result["extractions"] = extractions
    
    # Step 3: Reflector (간단한 코멘트)
    reflection = generate_reflection(result["clean_text"])
    if reflection:
        result["reflection"] = reflection
    
    return result
