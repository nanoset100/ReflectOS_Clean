"""
ReflectOS - Check-in
일상 기록 입력 (텍스트, 이미지, 음성)
Step 2: 규칙 기반 추출
Step 3: LLM 기반 구조화 (Extractor)
Step 4: 음성 STT
Step 5: 이미지 Vision
"""
import streamlit as st
import re
from typing import Dict, List, Optional
from datetime import datetime

st.set_page_config(page_title="Check-in - ReflectOS", page_icon="✍️", layout="wide")


# === 자동 인덱싱 토글 값 로드 ===
from lib.supabase_db import get_profile
_profile = get_profile()
_settings = (_profile or {}).get("settings") or {}
if "auto_index_on_save" not in st.session_state:
    st.session_state["auto_index_on_save"] = bool(_settings.get("auto_index_on_save", False))


# === 규칙 기반 Extraction (폴백용) ===
def extract_by_rules(content: str) -> Dict[str, List[str]]:
    """
    규칙 기반으로 텍스트에서 구조화된 정보 추출
    """
    lines = content.strip().split('\n')
    
    tasks = []
    obstacles = []
    projects = []
    insights = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # task: '-' 또는 '•'로 시작하는 줄
        if line.startswith('-') or line.startswith('•') or line.startswith('*'):
            task_text = line.lstrip('-•* ').strip()
            if task_text:
                tasks.append(task_text)
        
        # obstacle: '!' 시작 또는 부정적 키워드 포함
        obstacle_keywords = ['문제', '어려움', '힘들', '막혀', '안됨', '실패', '오류', '버그']
        if line.startswith('!') or any(kw in line for kw in obstacle_keywords):
            obstacle_text = line.lstrip('! ').strip()
            if obstacle_text and obstacle_text not in obstacles:
                obstacles.append(obstacle_text)
        
        # project: '#프로젝트명' 형태
        project_matches = re.findall(r'#(\w+)', line)
        for proj in project_matches:
            if proj not in projects:
                projects.append(proj)
        
        # insight: 인사이트 키워드 포함
        insight_keywords = ['💡', '인사이트', '배움', '깨달음', '발견', '아이디어']
        if any(kw in line for kw in insight_keywords):
            insight_text = line.strip()
            if insight_text and insight_text not in insights:
                insights.append(insight_text)
    
    return {
        "tasks": tasks,
        "obstacles": obstacles,
        "projects": projects,
        "insights": insights,
        "people": [],
        "emotions": []
    }


st.title("✍️ Check-in")
st.caption("오늘의 생각과 감정을 기록하세요")

# === 세션 상태 초기화 ===
if "transcribed_text" not in st.session_state:
    st.session_state.transcribed_text = ""
if "image_analysis" not in st.session_state:
    st.session_state.image_analysis = ""
if "uploaded_artifacts" not in st.session_state:
    st.session_state.uploaded_artifacts = []  # [{type, storage_path, metadata}]

# === 사이드바: AI 설정 ===
with st.sidebar:
    st.subheader("🤖 AI 설정")
    use_ai_extraction = st.toggle(
        "LLM 기반 구조화 사용",
        value=True,
        help="OpenAI를 사용하여 더 정확하게 정보를 추출합니다"
    )
    
    if use_ai_extraction:
        use_ingestor = st.checkbox(
            "텍스트 정리 (Ingestor)",
            value=False,
            help="텍스트를 정리/정규화한 후 분석"
        )
        generate_reflection = st.checkbox(
            "AI 코멘트 생성",
            value=True,
            help="체크인에 대한 짧은 AI 코멘트"
        )
    else:
        use_ingestor = False
        generate_reflection = False
    
    st.divider()
    st.caption("💡 LLM 미사용 시 규칙 기반으로 추출")


# === 멀티모달 입력 섹션 (Step 4, 5) ===
st.subheader("🎙️ 멀티모달 입력")

tab_audio, tab_image = st.tabs(["🎤 음성 입력", "🖼️ 이미지 입력"])

# --- 음성 입력 탭 (Step 4) ---
with tab_audio:
    st.markdown("**음성 파일을 업로드하면 텍스트로 변환됩니다**")
    
    audio_file = st.file_uploader(
        "음성 파일 선택",
        type=["mp3", "wav", "m4a", "ogg", "webm"],
        key="audio_uploader",
        help="지원 형식: MP3, WAV, M4A, OGG, WebM"
    )
    
    if audio_file is not None:
        # 오디오 미리보기
        st.audio(audio_file, format=f"audio/{audio_file.type.split('/')[-1]}")
        
        if st.button("🎯 음성 → 텍스트 변환", key="transcribe_btn"):
            with st.spinner("🔄 음성을 텍스트로 변환 중..."):
                try:
                    from lib.openai_client import transcribe_audio
                    from lib.supabase_storage import upload_file
                    from lib.supabase_db import insert_artifact
                    
                    # 1. Supabase Storage에 업로드
                    file_bytes = audio_file.getvalue()
                    content_type = audio_file.type or "audio/mpeg"
                    
                    storage_path = upload_file(
                        file_data=file_bytes,
                        file_name=audio_file.name,
                        content_type=content_type,
                        folder="audio"
                    )
                    
                    # 2. OpenAI Whisper로 전사
                    audio_file.seek(0)  # 파일 포인터 리셋
                    transcribed = transcribe_audio(audio_file, language="ko")
                    
                    if transcribed:
                        st.session_state.transcribed_text = transcribed
                        
                        # artifacts 정보 저장 (체크인 저장 시 DB에 기록)
                        st.session_state.uploaded_artifacts.append({
                            "type": "audio",
                            "storage_path": storage_path,
                            "original_name": audio_file.name,
                            "file_size": len(file_bytes),
                            "metadata": {
                                "transcription": transcribed,
                                "duration": None  # 향후 추가 가능
                            }
                        })
                        
                        st.success("✅ 음성 변환 완료!")
                    else:
                        st.error("음성 변환에 실패했습니다.")
                        
                except ImportError as e:
                    st.error(f"모듈 로드 실패: {e}")
                except Exception as e:
                    st.error(f"오류 발생: {e}")
    
    # 전사된 텍스트 표시 및 편집
    if st.session_state.transcribed_text:
        st.markdown("---")
        st.markdown("**📝 변환된 텍스트** (편집 가능)")
        edited_transcription = st.text_area(
            "전사 결과",
            value=st.session_state.transcribed_text,
            height=100,
            key="edit_transcription",
            label_visibility="collapsed"
        )
        st.session_state.transcribed_text = edited_transcription
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📋 본문에 추가", key="add_transcription"):
                st.session_state.add_to_content = st.session_state.transcribed_text
                st.success("본문에 추가됨! 아래 내용란을 확인하세요.")
        with col2:
            if st.button("🗑️ 전사 내용 삭제", key="clear_transcription"):
                st.session_state.transcribed_text = ""
                st.rerun()


# --- 이미지 입력 탭 (Step 5) ---
with tab_image:
    st.markdown("**이미지를 업로드하면 AI가 내용을 분석합니다**")
    
    image_file = st.file_uploader(
        "이미지 파일 선택",
        type=["png", "jpg", "jpeg", "webp"],
        key="image_uploader",
        help="지원 형식: PNG, JPG, JPEG, WebP"
    )
    
    if image_file is not None:
        # 이미지 미리보기
        st.image(image_file, caption="업로드된 이미지", use_container_width=True)
        
        if st.button("🔍 이미지 분석", key="analyze_image_btn"):
            with st.spinner("🔄 이미지 분석 중..."):
                try:
                    from lib.openai_client import analyze_image
                    from lib.supabase_storage import upload_file, get_public_url
                    import base64
                    
                    # 1. Supabase Storage에 업로드
                    file_bytes = image_file.getvalue()
                    content_type = image_file.type or "image/jpeg"
                    
                    storage_path = upload_file(
                        file_data=file_bytes,
                        file_name=image_file.name,
                        content_type=content_type,
                        folder="images"
                    )
                    
                    # 2. Base64로 인코딩하여 Vision API 호출
                    base64_image = base64.b64encode(file_bytes).decode('utf-8')
                    image_url = f"data:{content_type};base64,{base64_image}"
                    
                    # 분석 프롬프트
                    analysis_prompt = """이 이미지에서 다음을 추출해주세요:
1. 이미지에 보이는 텍스트/메모 내용
2. 할 일 목록이 있다면 추출
3. 전체적인 맥락 요약 (한 문장)

간결하게 요점만 정리해주세요."""
                    
                    analysis_result = analyze_image(image_url, analysis_prompt)
                    
                    if analysis_result:
                        st.session_state.image_analysis = analysis_result
                        
                        # artifacts 정보 저장
                        st.session_state.uploaded_artifacts.append({
                            "type": "image",
                            "storage_path": storage_path,
                            "original_name": image_file.name,
                            "file_size": len(file_bytes),
                            "metadata": {
                                "analysis": analysis_result
                            }
                        })
                        
                        st.success("✅ 이미지 분석 완료!")
                    else:
                        st.error("이미지 분석에 실패했습니다.")
                        
                except ImportError as e:
                    st.error(f"모듈 로드 실패: {e}")
                except Exception as e:
                    st.error(f"오류 발생: {e}")
    
    # 분석 결과 표시 및 편집
    if st.session_state.image_analysis:
        st.markdown("---")
        st.markdown("**📝 분석 결과** (편집 가능)")
        edited_analysis = st.text_area(
            "분석 결과",
            value=st.session_state.image_analysis,
            height=100,
            key="edit_analysis",
            label_visibility="collapsed"
        )
        st.session_state.image_analysis = edited_analysis
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📋 본문에 추가", key="add_analysis"):
                st.session_state.add_to_content = st.session_state.image_analysis
                st.success("본문에 추가됨! 아래 내용란을 확인하세요.")
        with col2:
            if st.button("🗑️ 분석 내용 삭제", key="clear_analysis"):
                st.session_state.image_analysis = ""
                st.rerun()


st.divider()

# === 체크인 폼 ===
with st.form("checkin_form"):
    # 무드 선택
    st.subheader("오늘 기분은 어떤가요?")
    mood = st.radio(
        "기분 선택",
        options=["great", "good", "neutral", "bad", "terrible"],
        format_func=lambda x: {
            "great": "😊 아주 좋음",
            "good": "🙂 좋음",
            "neutral": "😐 보통",
            "bad": "😔 안 좋음",
            "terrible": "😢 매우 안 좋음"
        }[x],
        horizontal=True,
        label_visibility="collapsed"
    )
    
    # 에너지 슬라이더
    st.subheader("⚡ 에너지 레벨")
    energy = st.slider(
        "현재 에너지 레벨",
        min_value=1,
        max_value=10,
        value=5,
        help="1: 매우 지침 ~ 10: 에너지 넘침"
    )
    
    st.divider()
    
    # 텍스트 입력 (멀티모달 결과 합치기)
    st.subheader("📝 무슨 생각을 하고 있나요?")
    st.caption("💡 팁: `-`로 시작하면 할 일로 추출, `#태그`로 프로젝트 분류")
    
    # 멀티모달에서 추가된 내용 합치기
    initial_content = ""
    if hasattr(st.session_state, 'add_to_content') and st.session_state.add_to_content:
        initial_content = st.session_state.add_to_content + "\n\n"
        st.session_state.add_to_content = ""  # 리셋
    
    content = st.text_area(
        "내용",
        value=initial_content,
        placeholder="""오늘 있었던 일, 느낀 점, 배운 것 등을 자유롭게 작성하세요...

예시:
- API 문서 작성 완료
- 회의 준비
#ReflectOS 프로젝트 진행 중
💡 작은 단위로 나눠서 하니까 집중이 잘 됨""",
        height=200,
        label_visibility="collapsed"
    )
    
    # 태그 입력
    tags_input = st.text_input(
        "태그 (쉼표로 구분)",
        placeholder="예: 업무, 건강, 아이디어",
    )
    
    st.divider()
    
    # 제출 버튼
    submitted = st.form_submit_button("💾 저장하기", use_container_width=True, type="primary")
    
    if submitted:
        if not content.strip():
            st.warning("내용을 입력해주세요!")
        else:
            # 태그 파싱
            tags = [t.strip() for t in tags_input.split(",") if t.strip()]
            
            # 멀티모달 텍스트 합치기
            combined_content = content
            if st.session_state.transcribed_text:
                combined_content += f"\n\n[🎤 음성 전사]\n{st.session_state.transcribed_text}"
            if st.session_state.image_analysis:
                combined_content += f"\n\n[🖼️ 이미지 분석]\n{st.session_state.image_analysis}"
            
            # 결과 저장용 변수
            extractions = None
            clean_text = combined_content
            ai_reflection = None
            extraction_type = "rule_based"
            
            # === AI 기반 처리 (Step 3) ===
            if use_ai_extraction:
                with st.spinner("🤖 AI가 분석 중..."):
                    try:
                        from lib.openai_client import (
                            ingest_text, 
                            extract_structured_data,
                            generate_reflection as gen_reflection
                        )
                        
                        # Ingestor (선택적)
                        if use_ingestor:
                            ingested = ingest_text(combined_content)
                            if ingested:
                                clean_text = ingested
                        
                        # Extractor (Structured Outputs)
                        llm_extractions = extract_structured_data(clean_text)
                        if llm_extractions:
                            extractions = llm_extractions
                            extraction_type = "llm_extractor"
                        
                        # Reflector (선택적)
                        if generate_reflection:
                            ai_reflection = gen_reflection(clean_text)
                        
                    except ImportError as e:
                        st.warning(f"⚠️ OpenAI 모듈 로드 실패: {e}")
                    except Exception as e:
                        st.warning(f"⚠️ AI 처리 중 오류 (규칙 기반으로 대체): {e}")
            
            # === 규칙 기반 폴백 ===
            if extractions is None:
                extractions = extract_by_rules(combined_content)
                extraction_type = "rule_based"
            
            # === DB 저장 ===
            try:
                from lib.supabase_db import insert_checkin, insert_extraction, insert_artifact
                
                # 체크인 저장
                checkin_data = insert_checkin(
                    content=content,  # 원본 텍스트만 저장
                    mood=mood,
                    tags=tags,
                    metadata={
                        "energy": energy,
                        "clean_text": clean_text if clean_text != content else None,
                        "has_audio": bool(st.session_state.transcribed_text),
                        "has_image": bool(st.session_state.image_analysis)
                    }
                )
                
                if checkin_data:
                    checkin_id = checkin_data.get("id")
                    
                    # artifacts 저장 (멀티모달)
                    for artifact in st.session_state.uploaded_artifacts:
                        insert_artifact(
                            checkin_id=checkin_id,
                            artifact_type=artifact["type"],
                            storage_path=artifact["storage_path"],
                            metadata=artifact.get("metadata"),
                            original_name=artifact.get("original_name"),
                            file_size=artifact.get("file_size")
                        )
                    
                    # extraction 저장
                    if any(extractions.values()):
                        insert_extraction(
                            source_type="checkin",
                            source_id=checkin_id,
                            extraction_type=extraction_type,
                            data=extractions
                        )
                    
                    st.success("✅ 체크인이 저장되었습니다!")
                    st.balloons()
                    
                    # === 자동 인덱싱 (토글 ON일 때만) ===
                    if st.session_state.get("auto_index_on_save", False):
                        from lib.config import get_openai_api_key
                        if not get_openai_api_key():
                            st.warning("⚠️ OpenAI API 키가 없어 자동 인덱싱을 건너뜁니다.")
                        else:
                            with st.spinner("🧠 자동 인덱싱 중..."):
                                try:
                                    from lib.rag import index_checkin, index_extraction
                                    
                                    # checkin 인덱싱: clean_text 우선(멀티모달/ingestor 반영)
                                    ok_checkin = index_checkin(checkin_id, clean_text, extractions)
                                    
                                    # extraction 인덱싱: 추출값이 비어있지 않을 때만
                                    ok_extraction = True
                                    try:
                                        if extractions and any(extractions.values()):
                                            ok_extraction = index_extraction(checkin_id, extraction_type, extractions)
                                    except Exception:
                                        ok_extraction = False
                                    
                                    if ok_checkin and ok_extraction:
                                        st.info("✅ 자동 인덱싱 완료 (Memory에서 즉시 검색 가능)")
                                    else:
                                        st.warning("⚠️ 자동 인덱싱 일부 실패 (체크인은 저장됨). 필요시 Memory에서 수동 동기화하세요.")
                                except Exception as e:
                                    st.warning(f"⚠️ 자동 인덱싱 오류 (체크인은 저장됨): {e}")
                    
                    # 세션 상태 초기화
                    st.session_state.transcribed_text = ""
                    st.session_state.image_analysis = ""
                    st.session_state.uploaded_artifacts = []
                    
                    # === 결과 표시 ===
                    with st.expander("📋 저장된 내용 확인", expanded=True):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**기본 정보**")
                            st.json({
                                "mood": mood,
                                "energy": energy,
                                "tags": tags,
                                "extraction_type": extraction_type,
                                "artifacts_count": len(st.session_state.uploaded_artifacts) if st.session_state.uploaded_artifacts else 0
                            })
                        
                        with col2:
                            st.markdown(f"**추출된 정보** (`{extraction_type}`)")
                            
                            if extractions.get("tasks"):
                                st.markdown("**📌 Tasks:**")
                                for task in extractions["tasks"]:
                                    st.markdown(f"  - {task}")
                            
                            if extractions.get("obstacles"):
                                st.markdown("**⚠️ Obstacles:**")
                                for obs in extractions["obstacles"]:
                                    st.markdown(f"  - {obs}")
                            
                            if extractions.get("projects"):
                                st.markdown(f"**📁 Projects:** {', '.join(extractions['projects'])}")
                            
                            if extractions.get("insights"):
                                st.markdown("**💡 Insights:**")
                                for ins in extractions["insights"]:
                                    st.markdown(f"  - {ins}")
                            
                            if extractions.get("people"):
                                st.markdown(f"**👥 People:** {', '.join(extractions['people'])}")
                            
                            if extractions.get("emotions"):
                                st.markdown(f"**😊 Emotions:** {', '.join(extractions['emotions'])}")
                            
                            if not any(extractions.values()):
                                st.caption("추출된 항목 없음")
                    
                    # AI 코멘트 표시
                    if ai_reflection:
                        st.divider()
                        st.subheader("💬 AI 코멘트")
                        st.info(ai_reflection)
                else:
                    st.error("저장 실패. 다시 시도해주세요.")
                    
            except ImportError as e:
                st.warning(f"⚠️ DB 모듈 로드 실패: {e}")
                # 데모 모드
                with st.expander("저장된 내용 (데모)", expanded=True):
                    st.json({
                        "mood": mood,
                        "energy": energy,
                        "content": content[:100] + "...",
                        "tags": tags,
                        "extractions": extractions,
                        "extraction_type": extraction_type
                    })
                if ai_reflection:
                    st.info(f"💬 AI: {ai_reflection}")
            except Exception as e:
                st.error(f"오류 발생: {e}")
