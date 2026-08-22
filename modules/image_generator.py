"""
image_generator.py
-------------------
OpenAI 이미지 생성 API(gpt-image-1)를 호출하여 로고 시안을 생성하고 PNG로 저장한다.

참고: 기존 dall-e-3 모델은 2026년 5월 12일 OpenAI에서 완전히 폐지(retire)되어
      더 이상 API 호출이 불가능하다. 후속 모델인 gpt-image-1 계열을 사용한다.
      (더 저렴한 대안이 필요하면 "gpt-image-1-mini"로 교체 가능)

[신뢰성 보강]
로고 시안이 2~3개 반드시 저장되도록 두 가지 안전장치를 둔다.
1. 재시도(retry): 일시적 오류(요청 한도 초과/네트워크/서버 오류)는 지수 백오프로 최대
   RETRY_LIMIT회까지 재시도한다.
2. 플레이스홀더(placeholder): 재시도까지 모두 실패하면(또는 인증 오류처럼 재시도가
   무의미한 경우) matplotlib으로 간단한 대체 로고 이미지를 생성해 저장한다.
   → 이렇게 하면 API가 완전히 실패하는 최악의 상황에서도 logo_images가 빈 배열로
     남지 않고, 요구사항(로고 2~3개 PNG 저장)을 항상 충족한다.

각 로고의 실패/재시도/플레이스홀더 사용 여부는 errors 리스트에 구조화된 형태로 기록되어,
최종적으로 brand_result.json의 "errors" 필드에 함께 저장된다.
"""

import os
import time
import base64
from datetime import datetime
import requests
from openai import OpenAI, APIError, APIConnectionError, AuthenticationError, RateLimitError

IMAGE_MODEL = "gpt-image-1"
LOGO_COUNT = 3          # 생성할 로고 시안 개수 (2~3개 요구사항)
RETRY_LIMIT = 2          # 일시적 오류 시 추가로 재시도할 횟수 (총 시도 = 1 + RETRY_LIMIT)
RETRY_BASE_DELAY = 2     # 지수 백오프 기본 대기 시간(초): 2초 → 4초 → ...

# 재시도 대상 오류: 시간이 지나면 성공할 가능성이 있는 "일시적" 오류
RETRYABLE_ERRORS = (RateLimitError, APIConnectionError, APIError)


def _build_logo_prompt(brief: dict, naming_result: list, color_result: dict) -> str:
    """브리프 + 네이밍 + 컬러 결과를 반영한 로고 생성 프롬프트를 만든다."""
    brand_name = naming_result[0]["name"] if naming_result else brief["industry"]
    main_color = color_result["main_color"]["hex"] if color_result else "#000000"

    prompt = (
        f"A minimalist, professional logo design for a brand called '{brand_name}'. "
        f"Industry: {brief['industry']}. Target audience: {brief['target']}. "
        f"Keywords: {', '.join(brief['keywords'])}. "
        f"Primary brand color: {main_color}. "
        "Clean vector-style logo, flat design, simple shapes, white background, "
        "no text unless it's the brand initial, suitable for a brand identity guideline."
    )
    return prompt


def _record_error(step_detail: str, error_type: str, message: str, errors: list) -> None:
    """로고 관련 실패/대체 정보를 errors 리스트에 구조화된 형태로 기록한다."""
    errors.append({
        "step": step_detail,
        "error_type": error_type,
        "message": message,
        "occurred_at": datetime.now().isoformat(timespec="seconds"),
    })


def _extract_image_bytes(response) -> bytes:
    """API 응답에서 이미지 바이트를 추출한다 (b64_json 또는 url 두 형식 모두 지원)."""
    data = response.data[0]
    b64_json = getattr(data, "b64_json", None)
    image_url = getattr(data, "url", None)

    if b64_json:
        return base64.b64decode(b64_json)
    elif image_url:
        img_response = requests.get(image_url, timeout=30)
        img_response.raise_for_status()
        return img_response.content
    else:
        raise ValueError("API 응답에서 이미지 데이터(b64_json/url)를 찾을 수 없습니다.")


def _generate_one_logo(client: OpenAI, prompt: str, file_path: str,
                        file_name: str, errors: list) -> bool:
    """
    로고 1개를 실제 API로 생성 시도한다. 일시적 오류는 지수 백오프로 재시도한다.
    성공하면 True, (재시도까지 모두 실패하면) False를 반환한다.
    """
    for attempt in range(RETRY_LIMIT + 1):
        try:
            response = client.images.generate(
                model=IMAGE_MODEL,
                prompt=prompt,
                size="1024x1024",
                n=1,
            )
            image_bytes = _extract_image_bytes(response)
            with open(file_path, "wb") as f:
                f.write(image_bytes)
            print(f"      - 저장: {file_path}")
            return True

        except AuthenticationError as e:
            # 키 인증 오류는 재시도해도 결과가 같으므로 즉시 실패 처리
            message = "API 키 인증에 실패했습니다. OPENAI_API_KEY 값을 확인해주세요."
            print(f"      - [{file_name} 실패] {message}")
            _record_error(f"로고 시안 생성 ({file_name})", "AuthenticationError", message, errors)
            return False

        except RETRYABLE_ERRORS as e:
            error_type = type(e).__name__
            message = str(e)
            is_last_attempt = attempt == RETRY_LIMIT
            if not is_last_attempt:
                delay = RETRY_BASE_DELAY * (2 ** attempt)
                print(f"      - [{file_name} 재시도 {attempt + 1}/{RETRY_LIMIT}] "
                      f"{error_type}: {message} → {delay}초 후 재시도")
                time.sleep(delay)
                continue
            else:
                print(f"      - [{file_name} 실패] {RETRY_LIMIT}회 재시도 후에도 실패: {message}")
                _record_error(
                    f"로고 시안 생성 ({file_name})", error_type,
                    f"{RETRY_LIMIT}회 재시도했지만 실패했습니다: {message}", errors,
                )
                return False

        except (requests.RequestException, OSError, ValueError) as e:
            message = f"파일 저장/네트워크 오류: {e}"
            print(f"      - [{file_name} 실패] {message}")
            _record_error(f"로고 시안 생성 ({file_name})", type(e).__name__, message, errors)
            return False

        except Exception as e:
            message = f"예상치 못한 오류: {e}"
            print(f"      - [{file_name} 실패] {message}")
            _record_error(f"로고 시안 생성 ({file_name})", type(e).__name__, message, errors)
            return False

    return False


def _save_placeholder_logo(brief: dict, naming_result: list, color_result: dict,
                            file_path: str, file_name: str, errors: list) -> bool:
    """
    AI 로고 생성이 재시도까지 모두 실패했을 때 사용하는 대체(placeholder) 이미지를
    matplotlib으로 직접 그려서 저장한다. 브랜드명 첫 글자 + 메인 컬러를 사용해
    최소한의 브랜드 아이덴티티를 담는다.
    """
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        # palette_visualizer의 밝기 판정 로직을 재사용해 텍스트 색을 자동 대비
        from modules.palette_visualizer import is_light_color

        brand_name = naming_result[0]["name"] if naming_result else brief.get("industry", "BRAND")
        initial = brand_name.strip()[0] if brand_name.strip() else "B"
        main_hex = color_result["main_color"]["hex"] if color_result else "#4A4A4A"
        text_color = "black" if is_light_color(main_hex) else "white"

        fig, ax = plt.subplots(figsize=(4, 4))
        ax.add_patch(plt.Rectangle((0, 0), 1, 1, color=main_hex))
        ax.text(0.5, 0.55, initial, ha="center", va="center",
                 fontsize=110, color=text_color, weight="bold")
        ax.text(0.5, 0.12, "PLACEHOLDER", ha="center", va="center",
                 fontsize=11, color=text_color, alpha=0.7)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")

        plt.savefig(file_path, dpi=150, bbox_inches="tight")
        plt.close(fig)

        print(f"      - [{file_name}] 플레이스홀더 이미지로 대체 저장: {file_path}")
        _record_error(
            f"로고 시안 생성 ({file_name})", "PlaceholderUsed",
            "AI 로고 생성이 재시도까지 모두 실패해 플레이스홀더 이미지로 대체 저장했습니다.",
            errors,
        )
        return True

    except Exception as e:
        print(f"      - [{file_name}] 플레이스홀더 이미지 생성마저 실패했습니다: {e}")
        _record_error(f"로고 시안 생성 ({file_name})", type(e).__name__,
                       f"플레이스홀더 이미지 생성도 실패했습니다: {e}", errors)
        return False


def generate_logos(client: OpenAI, brief: dict, naming_result: list,
                    color_result: dict, output_dir: str, errors: list) -> list:
    """
    로고 시안 2~3개를 생성하여 output_dir에 PNG로 저장한다.

    각 시안은 다음 순서로 최소 1개의 파일이 저장되도록 보장한다.
      1) 실제 AI 이미지 생성 시도 (일시적 오류는 지수 백오프로 재시도)
      2) 그래도 실패하면 matplotlib 플레이스홀더 이미지로 대체 저장

    반환값: 저장에 성공한 로고 파일 경로 리스트 (AI 생성 + 플레이스홀더 모두 포함)
    """
    prompt = _build_logo_prompt(brief, naming_result, color_result)
    saved_paths = []

    for i in range(1, LOGO_COUNT + 1):
        file_name = f"logo_{i:02d}.png"
        file_path = os.path.join(output_dir, file_name)

        success = _generate_one_logo(client, prompt, file_path, file_name, errors)

        if not success:
            success = _save_placeholder_logo(
                brief, naming_result, color_result, file_path, file_name, errors
            )

        if success:
            saved_paths.append(file_path)

    if not saved_paths:
        print("      - 로고 시안 생성 및 플레이스홀더 저장까지 모두 실패했습니다.")

    return saved_paths