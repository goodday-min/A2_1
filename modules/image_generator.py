"""
image_generator.py
-------------------
OpenAI 이미지 생성 API(gpt-image-1)를 호출하여 로고 시안을 생성하고 PNG로 저장한다.

참고: 기존 dall-e-3 모델은 2026년 5월 12일 OpenAI에서 완전히 폐지(retire)되어
      더 이상 API 호출이 불가능하다. 후속 모델인 gpt-image-1 계열을 사용한다.
      (더 저렴한 대안이 필요하면 "gpt-image-1-mini"로 교체 가능)
"""

import os
import base64
import requests
from openai import OpenAI, APIError, APIConnectionError, AuthenticationError, RateLimitError

IMAGE_MODEL = "gpt-image-1"
LOGO_COUNT = 3  # 생성할 로고 시안 개수 (2~3개 요구사항)


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


def generate_logos(client: OpenAI, brief: dict, naming_result: list,
                    color_result: dict, output_dir: str) -> list:
    """
    로고 시안 2~3개를 생성하여 output_dir에 PNG로 저장한다.
    각 시안 생성에 실패해도 나머지 시안 생성은 계속 진행한다.
    반환값: 저장에 성공한 로고 파일 경로 리스트
    """
    prompt = _build_logo_prompt(brief, naming_result, color_result)
    saved_paths = []

    for i in range(1, LOGO_COUNT + 1):
        file_name = f"logo_{i:02d}.png"
        try:
            response = client.images.generate(
                model=IMAGE_MODEL,
                prompt=prompt,
                size="1024x1024",
                n=1,
            )
            data = response.data[0]

            # SDK/모델 버전에 따라 b64_json 또는 url 중 하나로 결과가 온다.
            # (일부 버전은 response_format 파라미터 자체를 지원하지 않으므로
            #  파라미터를 넘기지 않고 두 경우를 모두 처리한다.)
            b64_json = getattr(data, "b64_json", None)
            image_url = getattr(data, "url", None)

            if b64_json:
                image_bytes = base64.b64decode(b64_json)
            elif image_url:
                img_response = requests.get(image_url, timeout=30)
                img_response.raise_for_status()
                image_bytes = img_response.content
            else:
                raise ValueError("API 응답에서 이미지 데이터(b64_json/url)를 찾을 수 없습니다.")

            file_path = os.path.join(output_dir, file_name)
            with open(file_path, "wb") as f:
                f.write(image_bytes)

            saved_paths.append(file_path)
            print(f"      - 저장: {file_path}")

        except AuthenticationError as e:
            print(f"      - [{file_name} 실패] API 키 인증에 실패했습니다. OPENAI_API_KEY 값을 확인해주세요.")
            print("        -> 이후 로고 생성 시도를 중단하고 다음 단계로 진행합니다.")
            break
        except RateLimitError as e:
            print(f"      - [{file_name} 실패] API 요청 한도를 초과했습니다: {e}")
            continue
        except APIConnectionError as e:
            print(f"      - [{file_name} 실패] 네트워크 연결에 실패했습니다: {e}")
            continue
        except APIError as e:
            print(f"      - [{file_name} 실패] OpenAI API 오류가 발생했습니다: {e}")
            continue
        except (requests.RequestException, OSError) as e:
            print(f"      - [{file_name} 실패] 파일 저장/네트워크 오류: {e}")
            continue
        except Exception as e:
            print(f"      - [{file_name} 실패] 예상치 못한 오류: {e}")
            continue

    if not saved_paths:
        print("      - 모든 로고 시안 생성에 실패했습니다. 텍스트 결과물은 정상적으로 저장됩니다.")

    return saved_paths