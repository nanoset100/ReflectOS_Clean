"""
ReflectOS - Supabase Storage 헬퍼
이미지/오디오 파일 업로드 및 관리
"""
import streamlit as st
from lib.config import get_supabase_client, get_current_user_id
from typing import Optional
import uuid
from datetime import datetime


BUCKET_NAME = "artifacts"  # Supabase Storage 버킷 이름


def upload_file(
    file_data: bytes,
    file_name: str,
    content_type: str,
    folder: str = "uploads"
) -> Optional[str]:
    """
    파일 업로드
    
    Args:
        file_data: 파일 바이너리 데이터
        file_name: 원본 파일명
        content_type: MIME 타입 (image/jpeg, audio/mp3 등)
        folder: 저장 폴더 (uploads, images, audio 등)
    
    Returns:
        storage_path: 저장된 경로 (없으면 None)
    """
    try:
        client = get_supabase_client()
        if not client:
            return None
        
        user_id = get_current_user_id()
        
        # 고유 파일명 생성
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        ext = file_name.split(".")[-1] if "." in file_name else "bin"
        storage_path = f"{user_id}/{folder}/{timestamp}_{unique_id}.{ext}"
        
        # 업로드
        response = client.storage.from_(BUCKET_NAME).upload(
            path=storage_path,
            file=file_data,
            file_options={"content-type": content_type}
        )
        
        return storage_path
        
    except Exception as e:
        st.error(f"파일 업로드 실패: {e}")
        return None


def get_public_url(storage_path: str) -> Optional[str]:
    """
    파일의 공개 URL 반환
    """
    try:
        client = get_supabase_client()
        if not client:
            return None
        
        response = client.storage.from_(BUCKET_NAME).get_public_url(storage_path)
        return response
        
    except Exception as e:
        return None


def delete_file(storage_path: str) -> bool:
    """
    파일 삭제
    """
    try:
        client = get_supabase_client()
        if not client:
            return False
        
        client.storage.from_(BUCKET_NAME).remove([storage_path])
        return True
        
    except Exception as e:
        st.error(f"파일 삭제 실패: {e}")
        return False


def list_files(folder: str = "uploads") -> list:
    """
    폴더 내 파일 목록 조회
    """
    try:
        client = get_supabase_client()
        if not client:
            return []
        
        user_id = get_current_user_id()
        path = f"{user_id}/{folder}"
        
        response = client.storage.from_(BUCKET_NAME).list(path)
        return response
        
    except Exception as e:
        return []

