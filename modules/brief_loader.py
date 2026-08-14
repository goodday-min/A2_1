"""
brief_loader.py
----------------
브랜드 브리프 JSON 파일을 읽고 유효성을 검사하는 모듈.

필수 필드: industry(업종), target(타겟), keywords(키워드)
선택 필드: tone(톤앤매너), competitors(경쟁사), notes(추가 요청사항)
"""

import json
import os

REQUIRED_FIELDS = ["industry", "target", "keywords"]
OPTIONAL_FIELDS = ["tone", "competitors", "notes"]


class BriefError(Exception):
    """브리프 파일 로딩/검증 오류"""
    pass


def load_brief(file_path: str) -> dict:
    """
    브랜드 브리프 JSON 파일을 읽어 dict로 반환한다.
    파일이 없거나, JSON 형식이 잘못되었거나, 필수 필드가 없으면 BriefError를 발생시킨다.
    """
    if not os.path.exists(file_path):
        raise BriefError(f"브리프 파일을 찾을 수 없습니다: {file_path}")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise BriefError(f"브리프 파일이 올바른 JSON 형식이 아닙니다: {e}")

    missing = [field for field in REQUIRED_FIELDS if field not in data or not data[field]]
    if missing:
        raise BriefError(
            f"브리프 파일에 필수 필드가 누락되었습니다: {', '.join(missing)}\n"
            f"필수 필드: {', '.join(REQUIRED_FIELDS)}"
        )

    # keywords는 리스트 또는 콤마로 구분된 문자열 모두 허용
    if isinstance(data["keywords"], str):
        data["keywords"] = [k.strip() for k in data["keywords"].split(",") if k.strip()]

    # 선택 필드 기본값 채우기
    for field in OPTIONAL_FIELDS:
        data.setdefault(field, "")

    return data
