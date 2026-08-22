"""
text_generator.py
------------------
OpenAI GPT API를 호출하여 브랜드 네이밍, 슬로건, 스토리, 컬러 팔레트(텍스트 정보)를 생성한다.

요구사항 9번(에러 처리)에 따라 각 함수는 API 호출이 실패해도 예외를 던져서 전체 프로그램을
멈추게 하지 않는다. 대신 에러 메시지를 콘솔에 출력하고, 실패 정보를 errors 리스트에 구조화된
형태로 기록한 뒤 None을 반환하여, 호출부(main.py)가 다음 단계로 계속 진행할 수 있도록 한다.
이 errors 리스트는 최종적으로 brand_result.json에 함께 저장된다.
"""

import json
from datetime import datetime
from openai import OpenAI, APIError, APIConnectionError, AuthenticationError, RateLimitError

TEXT_MODEL = "gpt-4o-mini"


def _build_brief_context(brief: dict) -> str:
    """브리프 정보를 프롬프트에 넣기 좋은 문자열로 정리"""
    lines = [
        f"업종(industry): {brief['industry']}",
        f"타겟(target): {brief['target']}",
        f"키워드(keywords): {', '.join(brief['keywords'])}",
    ]
    if brief.get("tone"):
        lines.append(f"톤앤매너(tone): {brief['tone']}")
    if brief.get("competitors"):
        lines.append(f"경쟁사(competitors): {brief['competitors']}")
    if brief.get("notes"):
        lines.append(f"추가 요청사항(notes): {brief['notes']}")
    return "\n".join(lines)


def _call_json(client: OpenAI, system_prompt: str, user_prompt: str) -> dict:
    """
    OpenAI Chat Completions API를 JSON 모드로 호출하는 공통 함수.
    실패 시 예외를 상위로 전달하지 않고, 이 함수를 호출한 쪽에서 try/except로 처리한다.
    """
    response = client.chat.completions.create(
        model=TEXT_MODEL,
        response_format={"type": "json_object"},
        temperature=0.9,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    content = response.choices[0].message.content
    return json.loads(content)


def _handle_api_error(step_name: str, error: Exception, errors: list) -> None:
    """
    API 오류 종류에 따라 사용자에게 보여줄 안내 메시지를 콘솔에 출력하고,
    동시에 errors 리스트에 구조화된 오류 기록을 추가한다.
    (errors 리스트는 main.py에서 생성되어 각 생성 함수에 공유되며,
     최종적으로 result_saver.py를 통해 brand_result.json의 "errors" 필드에 저장된다.)
    """
    if isinstance(error, AuthenticationError):
        error_type = "AuthenticationError"
        message = "API 키 인증에 실패했습니다. OPENAI_API_KEY 값을 확인해주세요."
    elif isinstance(error, RateLimitError):
        error_type = "RateLimitError"
        message = "API 요청 한도(rate limit)를 초과했습니다. 잠시 후 다시 시도해주세요."
    elif isinstance(error, APIConnectionError):
        error_type = "APIConnectionError"
        message = "네트워크 연결에 실패했습니다. 인터넷 연결 상태를 확인해주세요."
    elif isinstance(error, APIError):
        error_type = "APIError"
        message = f"OpenAI API 오류가 발생했습니다: {error}"
    elif isinstance(error, json.JSONDecodeError):
        error_type = "JSONDecodeError"
        message = f"AI 응답을 JSON으로 해석하지 못했습니다: {error}"
    else:
        error_type = type(error).__name__
        message = f"예상치 못한 오류가 발생했습니다: {error}"

    print(f"      - [{step_name} 실패] {message}")
    print(f"        -> {step_name} 단계를 건너뛰고 다음 단계를 계속 진행합니다.")

    errors.append({
        "step": step_name,
        "error_type": error_type,
        "message": message,
        "occurred_at": datetime.now().isoformat(timespec="seconds"),
    })


def generate_naming(client: OpenAI, brief: dict, errors: list) -> list | None:
    """브랜드명 후보 3~5개와 각 이름의 의미/유래를 생성한다."""
    system_prompt = (
        "당신은 전문 브랜드 네이밍 컨설턴트입니다. 반드시 JSON 객체로만 응답하세요."
    )
    user_prompt = (
        f"{_build_brief_context(brief)}\n\n"
        "위 브랜드 브리프를 바탕으로 브랜드명 후보를 3~5개 제안해주세요.\n"
        "각 후보의 의미/유래는 반드시 공백 포함 15자를 넘지 않는 아주 짧은 구(句)로 "
        "요약해주세요. (예: '자연에서 피어나는 아름다움', '도시 속 자연의 싱그러움')\n"
        "완전한 문장이 아니라 명사구로 끝내고, 말줄임표(...)나 마침표를 사용하지 마세요.\n"
        "15자를 넘는 설명은 절대 작성하지 마세요. 15자 제한을 지키지 못할 바엔 "
        "더 짧고 간단한 표현으로 바꿔서 작성하세요.\n"
        "브랜드명에 영문 표기를 함께 쓰면 자연스러운 경우, "
        "'한글이름 (English Name)' 형태로 name에 표기해도 좋습니다 (필수는 아님).\n"
        '다음 JSON 형식으로만 응답하세요: '
        '{"names": [{"name": "브랜드명", "meaning": "15자 이내 짧은 구"}]}'
    )
    try:
        result = _call_json(client, system_prompt, user_prompt)
        return result.get("names", [])
    except Exception as e:
        _handle_api_error("브랜드 네이밍 생성", e, errors)
        return None


def generate_slogans(client: OpenAI, brief: dict, errors: list) -> list | None:
    """슬로건/태그라인 3개를 생성한다."""
    system_prompt = (
        "당신은 전문 카피라이터입니다. 반드시 JSON 객체로만 응답하세요."
    )
    user_prompt = (
        f"{_build_brief_context(brief)}\n\n"
        "위 브랜드 브리프의 톤앤매너에 맞는 슬로건/태그라인을 3개 만들어주세요.\n"
        '다음 JSON 형식으로만 응답하세요: {"slogans": ["슬로건1", "슬로건2", "슬로건3"]}'
    )
    try:
        result = _call_json(client, system_prompt, user_prompt)
        return result.get("slogans", [])
    except Exception as e:
        _handle_api_error("슬로건 생성", e, errors)
        return None


def generate_story(client: OpenAI, brief: dict, errors: list) -> str | None:
    """브랜드 스토리(300자 내외, 탄생 배경/철학/비전)를 생성한다."""
    system_prompt = (
        "당신은 전문 브랜드 스토리텔러입니다. 반드시 JSON 객체로만 응답하세요."
    )
    user_prompt = (
        f"{_build_brief_context(brief)}\n\n"
        "위 브랜드 브리프를 바탕으로 브랜드 스토리를 작성해주세요.\n"
        "탄생 배경, 철학, 비전을 포함하여 한국어 기준 300자 내외로 작성해주세요.\n"
        '다음 JSON 형식으로만 응답하세요: {"story": "브랜드 스토리 내용"}'
    )
    try:
        result = _call_json(client, system_prompt, user_prompt)
        return result.get("story", "")
    except Exception as e:
        _handle_api_error("브랜드 스토리 생성", e, errors)
        return None


def generate_color_palette(client: OpenAI, brief: dict, errors: list) -> dict | None:
    """메인 컬러 1개, 서브 컬러 2~3개를 HEX 코드로 추천받는다."""
    system_prompt = (
        "당신은 전문 브랜드 컬러 디자이너입니다. 반드시 JSON 객체로만 응답하세요. "
        "색상 코드는 반드시 '#RRGGBB' 형식의 HEX 코드로만 제공하세요."
    )
    user_prompt = (
        f"{_build_brief_context(brief)}\n\n"
        "위 브랜드 브리프에 어울리는 컬러 팔레트를 추천해주세요.\n"
        "메인 컬러 1개, 서브 컬러 2~3개를 제안하고, 각 색상을 선택한 이유도 간단히 설명해주세요.\n"
        "각 색상의 name은 'Forest Green'처럼 영문 색상 이름으로 표기해주세요.\n"
        '다음 JSON 형식으로만 응답하세요: '
        '{"main_color": {"hex": "#RRGGBB", "name": "색상 이름", "reason": "선택 이유"}, '
        '"sub_colors": [{"hex": "#RRGGBB", "name": "색상 이름", "reason": "선택 이유"}]}'
    )
    try:
        result = _call_json(client, system_prompt, user_prompt)
        return result
    except Exception as e:
        _handle_api_error("컬러 팔레트 생성", e, errors)
        return None