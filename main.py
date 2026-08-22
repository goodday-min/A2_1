"""
main.py
-------
AI 브랜드 디자인 생성기 - CLI 진입점

실행 방법:
    python main.py

흐름:
    1. 사용자로부터 브리프 파일 경로, 출력 폴더 경로를 입력받는다.
    2. 브리프 JSON을 읽어 검증한다.
    3. [1/5] OpenAI GPT API로 브랜드 네이밍을 생성한다.
    4. [2/5] OpenAI GPT API로 슬로건을 생성한다.
    5. [3/5] OpenAI GPT API로 브랜드 스토리를 생성한다.
    6. [4/5] OpenAI GPT API로 컬러 팔레트를 생성하고 시각화하여 저장한다.
    7. [5/5] OpenAI gpt-image-1 API로 로고 시안을 생성한다.
    8. 모든 결과(성공한 항목 + 단계별 실패 기록)를 output 폴더에 저장한다.

출력 형식은 '실행 결과 예시' 문서를 기준으로 맞춰져 있다 (단계 번호, 들여쓰기, 요약 출력).
"""

import os
import sys
from datetime import datetime

from openai import OpenAI

from modules.config import get_openai_api_key
from modules.brief_loader import load_brief, BriefError
from modules.text_generator import (
    generate_naming,
    generate_slogans,
    generate_story,
    generate_color_palette,
)
from modules.image_generator import generate_logos
from modules.palette_visualizer import save_palette_image
from modules.result_saver import save_json_result

TOTAL_STEPS = 5


def print_banner():
    print()
    print("    🎨 AI 브랜드 아이덴티티 생성기")
    print()


def get_user_input() -> tuple[str, str]:
    """대화형으로 브리프 파일 경로와 출력 폴더 경로를 입력받는다."""
    brief_path = input("    브리프 파일 경로를 입력하세요: ").strip()
    while not brief_path:
        print("    브리프 파일 경로는 필수 입력값입니다.")
        brief_path = input("    브리프 파일 경로를 입력하세요: ").strip()

    output_dir = input("    출력 폴더 경로를 입력하세요 (엔터 시 ./output): ").strip()
    if not output_dir:
        output_dir = "./output"

    return brief_path, output_dir


def print_naming_result(naming):
    if not naming:
        print("      - 네이밍 생성에 실패했습니다.")
        return
    MAX_LEN = 15  # 한 줄 표시를 위한 의미 설명 최대 길이 (안전장치, 15자 이내)
    for item in naming:
        name = item.get("name", "")
        meaning = item.get("meaning", "")
        if len(meaning) > MAX_LEN:
            meaning = meaning[:MAX_LEN].rstrip() + "..."
        print(f"      - {name}: {meaning}")


def print_slogans_result(slogans):
    if not slogans:
        print("      - 슬로건 생성에 실패했습니다.")
        return
    for s in slogans:
        print(f'      - "{s}"')


def print_story_result(story):
    if not story:
        print("      - 스토리 생성에 실패했습니다.")
        return
    print(f"      - 스토리 생성 완료 ({len(story)}자)")


def print_color_result(colors):
    if not colors:
        print("      - 컬러 팔레트 생성에 실패했습니다.")
        return
    main_color = colors.get("main_color", {})
    sub_colors = colors.get("sub_colors", [])
    main_hex = main_color.get("hex", "-")
    main_name = main_color.get("name", "")
    if main_name:
        print(f"      - 메인: {main_hex} ({main_name})")
    else:
        print(f"      - 메인: {main_hex}")
    sub_hex_list = ", ".join(c.get("hex", "-") for c in sub_colors)
    print(f"      - 서브: {sub_hex_list}")


def main():
    print_banner()

    # API 키 확인 (없으면 여기서 안내 메시지 출력 후 종료)
    api_key = get_openai_api_key()
    client = OpenAI(api_key=api_key)

    # 사용자 입력
    brief_path, output_dir = get_user_input()
    print()

    # 브리프 로딩 및 검증
    try:
        brief = load_brief(brief_path)
    except BriefError as e:
        print(f"\n[브리프 오류] {e}")
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    # 각 단계의 실패 정보를 모아두는 리스트 (최종적으로 brand_result.json의 "errors" 필드에 저장됨)
    errors = []

    # [1/5] 브랜드 네이밍 생성
    print(f"    [1/{TOTAL_STEPS}] 브랜드 네이밍 생성 중...")
    naming = generate_naming(client, brief, errors)
    print_naming_result(naming)

    # [2/5] 슬로건 생성
    print(f"    [2/{TOTAL_STEPS}] 슬로건 생성 중...")
    slogans = generate_slogans(client, brief, errors)
    print_slogans_result(slogans)

    # [3/5] 브랜드 스토리 생성
    print(f"    [3/{TOTAL_STEPS}] 브랜드 스토리 생성 중...")
    story = generate_story(client, brief, errors)
    print_story_result(story)

    # [4/5] 컬러 팔레트 생성 + 시각화 저장
    print(f"    [4/{TOTAL_STEPS}] 컬러 팔레트 생성 중...")
    colors = generate_color_palette(client, brief, errors)
    print_color_result(colors)
    if colors:
        palette_path = save_palette_image(colors, output_dir)
        if palette_path:
            print(f"      - 저장: {palette_path}")
        else:
            errors.append({
                "step": "컬러 팔레트 이미지 저장",
                "error_type": "PaletteImageError",
                "message": "컬러 팔레트 PNG 저장에 실패했습니다.",
                "occurred_at": datetime.now().isoformat(timespec="seconds"),
            })

    # [5/5] 로고 시안 생성 (gpt-image-1)
    print(f"    [5/{TOTAL_STEPS}] 로고 시안 생성 중...")
    logo_paths = generate_logos(client, brief, naming, colors, output_dir, errors)

    # 최종 JSON 결과 저장 (성공한 결과 + 단계별 실패 기록 모두 포함)
    save_json_result(brief, naming, slogans, story, colors, logo_paths, output_dir, errors)

    print()
    if errors:
        print(f"    ⚠️  일부 단계가 실패했습니다 ({len(errors)}건). brand_result.json의 \"errors\" 필드를 확인하세요.")
    print(f"    ✅ 완료! {output_dir}/ 폴더를 확인하세요.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n사용자에 의해 프로그램이 중단되었습니다.")
        sys.exit(0)