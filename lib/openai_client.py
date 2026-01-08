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


# ============================================================
# STT 안정화를 위한 헬퍼 함수들 (FFmpeg WAV fallback 포함)
# ============================================================

import os
import shutil
import subprocess
import tempfile

# OpenAI Whisper가 지원하는 확장자 목록
ALLOWED_EXTENSIONS = {"flac", "m4a", "mp3", "mp4", "mpeg", "mpga", "oga", "ogg", "wav", "webm"}

# 확장자 → MIME 타입 매핑
EXT_TO_MIME = {
    "flac": "audio/flac",
    "m4a": "audio/mp4",
    "mp3": "audio/mpeg",
    "mp4": "audio/mp4",
    "mpeg": "audio/mpeg",
    "mpga": "audio/mpeg",
    "oga": "audio/ogg",
    "ogg": "audio/ogg",
    "wav": "audio/wav",
    "webm": "audio/webm",
}

# MIME 타입 → 확장자 매핑
MIME_TO_EXT = {
    "audio/flac": "flac",
    "audio/x-flac": "flac",
    "audio/mp4": "m4a",
    "audio/x-m4a": "m4a",
    "audio/m4a": "m4a",
    "audio/mpeg": "mp3",
    "audio/mp3": "mp3",
    "audio/ogg": "ogg",
    "audio/vorbis": "ogg",
    "audio/wav": "wav",
    "audio/x-wav": "wav",
    "audio/wave": "wav",
    "audio/webm": "webm",
    "video/webm": "webm",
}


def _has_ffmpeg() -> bool:
    """FFmpeg 설치 여부 확인"""
    return shutil.which("ffmpeg") is not None


def _to_wav_16k_mono(audio_bytes: bytes, in_ext: str) -> bytes:
    """
    FFmpeg를 사용하여 오디오를 WAV(16kHz, mono, PCM) 포맷으로 변환
    
    Args:
        audio_bytes: 원본 오디오 바이트
        in_ext: 입력 파일 확장자 (m4a, mp3 등)
    
    Returns:
        WAV 포맷 바이트
    
    Raises:
        RuntimeError: FFmpeg 미설치 또는 변환 실패
    """
    if not _has_ffmpeg():
        raise RuntimeError(
            "FFmpeg가 설치되어 있지 않습니다. WAV 변환을 위해 설치가 필요합니다.\n"
            "설치 방법:\n"
            "  - Ubuntu/Debian: sudo apt-get update && sudo apt-get install -y ffmpeg\n"
            "  - macOS: brew install ffmpeg\n"
            "  - Windows: https://ffmpeg.org/download.html 에서 다운로드"
        )
    
    # 임시 디렉토리에서 변환 수행
    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = os.path.join(tmpdir, f"input.{in_ext}")
        output_path = os.path.join(tmpdir, "output.wav")
        
        # 입력 파일 저장
        with open(input_path, "wb") as f:
            f.write(audio_bytes)
        
        # FFmpeg 명령 실행: 16kHz, mono, PCM WAV
        cmd = [
            "ffmpeg", "-y",
            "-i", input_path,
            "-ac", "1",          # mono
            "-ar", "16000",      # 16kHz
            "-f", "wav",         # WAV 포맷
            output_path
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=60  # 60초 타임아웃
            )
        except subprocess.TimeoutExpired:
            raise RuntimeError("FFmpeg 변환 시간 초과 (60초)")
        except Exception as e:
            raise RuntimeError(f"FFmpeg 실행 실패: {e}")
        
        if result.returncode != 0:
            # stderr 마지막 800자
            stderr_tail = result.stderr.decode("utf-8", errors="replace")[-800:]
            raise RuntimeError(f"FFmpeg 변환 실패 (exit={result.returncode}):\n{stderr_tail}")
        
        # 출력 파일 읽기
        if not os.path.exists(output_path):
            raise RuntimeError("FFmpeg 출력 파일이 생성되지 않음")
        
        with open(output_path, "rb") as f:
            return f.read()


def _sanitize_filename(name: str) -> str:
    """
    파일명에서 위험 문자 제거, ASCII 안전한 이름 반환
    
    Args:
        name: 원본 파일명
    
    Returns:
        안전한 파일명 (경로 제거, 특수문자 제거)
    """
    from pathlib import Path
    import re
    
    # 경로에서 파일명만 추출
    basename = Path(name).name
    
    # 위험 문자 제거 (알파벳, 숫자, 점, 언더스코어, 하이픈만 허용)
    safe_name = re.sub(r'[^a-zA-Z0-9._-]', '_', basename)
    
    # 빈 문자열이면 기본값
    if not safe_name or safe_name == '_':
        safe_name = "audio_upload"
    
    return safe_name


def _sniff_ext_from_magic(data: bytes) -> Optional[str]:
    """
    파일 매직넘버(시그니처)로 확장자 추론
    
    Args:
        data: 오디오 파일 바이트 (최소 12바이트 권장)
    
    Returns:
        추론된 확장자 (없으면 None)
    """
    if len(data) < 4:
        return None
    
    # WAV: RIFF....WAVE
    if data[:4] == b'RIFF' and len(data) >= 12 and data[8:12] == b'WAVE':
        return "wav"
    
    # FLAC: fLaC
    if data[:4] == b'fLaC':
        return "flac"
    
    # OGG: OggS
    if data[:4] == b'OggS':
        return "ogg"
    
    # MP3: ID3 태그 또는 프레임 동기
    if data[:3] == b'ID3':
        return "mp3"
    if len(data) >= 2 and data[0] == 0xFF and (data[1] & 0xE0) == 0xE0:
        return "mp3"
    
    # MP4/M4A: ftyp 박스 확인
    if len(data) >= 8 and data[4:8] == b'ftyp':
        return "m4a"
    
    # WebM: EBML 시그니처 (0x1A45DFA3)
    if len(data) >= 4 and data[:4] == b'\x1a\x45\xdf\xa3':
        return "webm"
    
    return None


def normalize_audio_meta(
    audio_bytes: bytes,
    filename: Optional[str] = None,
    mimetype: Optional[str] = None
) -> tuple:
    """
    오디오 메타데이터 정규화: 파일명/확장자/MIME 타입을 확정
    
    우선순위:
    1. filename 확장자 신뢰
    2. mimetype에서 확장자 추론
    3. magic sniff로 확장자 추론
    4. fallback: wav
    
    Args:
        audio_bytes: 오디오 파일 바이트
        filename: 원본 파일명 (optional)
        mimetype: MIME 타입 (optional)
    
    Returns:
        (normalized_filename, normalized_mimetype, extension)
    """
    ext = None
    
    # 1) filename 확장자에서 추출 시도
    if filename:
        from pathlib import Path
        suffix = Path(filename).suffix.lower().lstrip('.')
        if suffix in ALLOWED_EXTENSIONS:
            ext = suffix
    
    # 2) mimetype에서 확장자 추론
    if not ext and mimetype:
        mime_lower = mimetype.lower().strip()
        ext = MIME_TO_EXT.get(mime_lower)
    
    # 3) magic sniff
    if not ext:
        ext = _sniff_ext_from_magic(audio_bytes)
    
    # 4) fallback
    if not ext:
        ext = "wav"  # 최후 수단
    
    # 정규화된 파일명/MIME 생성
    base_name = _sanitize_filename(filename) if filename else "audio_upload"
    
    # 확장자가 없거나 다르면 교체
    from pathlib import Path
    current_suffix = Path(base_name).suffix.lower().lstrip('.')
    if current_suffix != ext:
        base_name = Path(base_name).stem + f".{ext}"
    
    normalized_filename = base_name
    normalized_mimetype = EXT_TO_MIME.get(ext, "audio/wav")
    
    return (normalized_filename, normalized_mimetype, ext)


def transcribe_audio_bytes(
    audio_bytes: bytes,
    filename: Optional[str] = None,
    mimetype: Optional[str] = None,
    language: str = "ko",
    prompt: Optional[str] = None
) -> str:
    """
    바이트 데이터로 음성을 텍스트로 변환 (Whisper) - 100% 안정화 버전
    
    - STT_FORCE_WAV=1 환경변수 설정 시 항상 WAV 변환 후 STT
    - 기본: 원본 시도 → Invalid file format 시 WAV fallback
    
    Args:
        audio_bytes: 오디오 파일의 바이트 데이터
        filename: 원본 파일명 (확장자 추출용, optional)
        mimetype: MIME 타입 (optional)
        language: 언어 코드 (기본: ko)
        prompt: 전사 힌트 프롬프트 (optional)
    
    Returns:
        변환된 텍스트
    
    Raises:
        RuntimeError: STT 실패 시 상세 정보 포함
    """
    # 메타데이터 정규화
    norm_filename, norm_mimetype, ext = normalize_audio_meta(audio_bytes, filename, mimetype)
    bytes_len = len(audio_bytes)
    
    # OpenAI 클라이언트 확인
    client = get_openai_client()
    if not client:
        raise RuntimeError(
            f"OpenAI API 키 미설정 | filename={norm_filename}, mimetype={norm_mimetype}, bytes_len={bytes_len}"
        )
    
    # 내부 헬퍼: OpenAI STT 호출
    def _call_openai_stt(data: bytes, name: str, mt: str) -> str:
        file_tuple = (name, data, mt)
        params = {
            "model": "whisper-1",
            "file": file_tuple,
            "language": language,
        }
        if prompt:
            params["prompt"] = prompt
        response = client.audio.transcriptions.create(**params)
        return response.text
    
    # WAV 변환 헬퍼
    def _convert_and_stt() -> str:
        """WAV로 변환 후 STT 호출"""
        from pathlib import Path
        wav_bytes = _to_wav_16k_mono(audio_bytes, ext)
        wav_name = Path(norm_filename).stem + ".wav"
        return _call_openai_stt(wav_bytes, wav_name, "audio/wav")
    
    # 환경변수: STT_FORCE_WAV=1 이면 항상 WAV 변환
    force_wav = os.environ.get("STT_FORCE_WAV", "0") == "1"
    
    if force_wav and ext != "wav":
        # 강제 WAV 변환 모드
        try:
            return _convert_and_stt()
        except Exception as e:
            raise RuntimeError(
                f"STT 실패 (강제 WAV 변환 모드): {e} | "
                f"filename={norm_filename}, mimetype={norm_mimetype}, bytes_len={bytes_len}"
            )
    
    # 기본 흐름: 원본 시도 → 실패 시 WAV fallback
    try:
        return _call_openai_stt(audio_bytes, norm_filename, norm_mimetype)
        
    except Exception as original_error:
        error_str = str(original_error).lower()
        
        # "Invalid file format" 에러인 경우 WAV fallback 시도
        if "invalid file format" in error_str and ext != "wav":
            try:
                return _convert_and_stt()
            except Exception as fallback_error:
                raise RuntimeError(
                    f"STT 실패 (원본 + WAV fallback 모두 실패)\n"
                    f"원본 에러: {original_error}\n"
                    f"WAV 변환 에러: {fallback_error}\n"
                    f"| filename={norm_filename}, mimetype={norm_mimetype}, bytes_len={bytes_len}"
                )
        
        # 그 외 에러는 그대로 전달
        raise RuntimeError(
            f"STT 실패: {original_error} | "
            f"filename={norm_filename}, mimetype={norm_mimetype}, bytes_len={bytes_len}"
        )


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
