"""
result_saver.py
----------------
텍스트 생성 결과를 brand_result.json 파일로 저장한다.
(이미지 파일은 image_generator.py, palette_visualizer.py에서 각각 저장됨)

각 단계에서 수집된 실패 정보(errors 리스트)도 함께 저장하여, 결과 파일만 보고도
어떤 단계가 왜 실패했는지 사후에 확인할 수 있도록 한다.
"""

import json
import os
from datetime import datetime


def save_json_result(brief: dict, naming: list | None, slogans: list | None,
                      story: str | None, colors: dict | None,
                      logo_paths: list, output_dir: str, errors: list | None = None) -> str:
    """모든 텍스트 결과, 생성된 파일 목록, 단계별 실패 기록을 brand_result.json으로 저장한다."""
    os.makedirs(output_dir, exist_ok=True)

    result = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "brief": brief,
        "naming": naming or [],
        "slogans": slogans or [],
        "story": story or "",
        "colors": colors or {},
        "generated_files": {
            "color_palette_image": "color_palette.png",
            "logo_images": [os.path.basename(p) for p in logo_paths],
        },
        "errors": errors or [],
    }

    file_path = os.path.join(output_dir, "brand_result.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    return file_path