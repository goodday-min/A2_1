"""
palette_visualizer.py
----------------------
생성된 컬러 팔레트(메인/서브 컬러)를 matplotlib으로 시각화하여 PNG 이미지로 저장한다.
"""

import os
import matplotlib
matplotlib.use("Agg")  # GUI 없는 환경(서버/CLI)에서도 동작하도록 백엔드 고정
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm


def _set_korean_font():
    """
    한글이 깨지지 않도록 시스템에 설치된 한글 폰트를 자동으로 찾아 적용한다.
    (윈도우: 맑은 고딕, macOS: AppleGothic, Linux: Noto Sans CJK / NanumGothic 등)
    적합한 폰트가 없으면 기본 폰트로 진행하고, 이 경우 한글 라벨이 네모(□)로 보일 수 있다.
    """
    candidates = [
        "Malgun Gothic", "AppleGothic", "NanumGothic",
        "Noto Sans CJK KR", "Noto Sans KR",
    ]
    installed = {f.name for f in fm.fontManager.ttflist}
    for name in candidates:
        if name in installed:
            plt.rcParams["font.family"] = name
            return
    # 후보 폰트가 fontManager에 이름으로 안 잡히는 경우, 파일 경로로 직접 등록 시도
    for font_path in fm.findSystemFonts():
        lower = font_path.lower()
        if "notosanscjk" in lower.replace(" ", "").replace("-", "") or "nanumgothic" in lower:
            fm.fontManager.addfont(font_path)
            plt.rcParams["font.family"] = fm.FontProperties(fname=font_path).get_name()
            return


_set_korean_font()
plt.rcParams["axes.unicode_minus"] = False


def save_palette_image(color_result: dict, output_dir: str,
                        file_name: str = "color_palette.png") -> str | None:
    """
    color_result 예시:
    {
      "main_color": {"hex": "#3A7CA5", "name": "딥 블루", "reason": "..."},
      "sub_colors": [{"hex": "#D9C9A3", "name": "샌드 베이지", "reason": "..."}, ...]
    }
    성공 시 저장된 파일 경로를, 실패 시 None을 반환한다.
    """
    if not color_result:
        print("      - [컬러 팔레트 이미지 저장 실패] 컬러 데이터가 없어 이미지를 생성할 수 없습니다.")
        return None

    try:
        colors = [color_result["main_color"]] + color_result.get("sub_colors", [])
        n = len(colors)

        fig, ax = plt.subplots(figsize=(2.2 * n, 3))

        for i, color in enumerate(colors):
            hex_code = color.get("hex", "#CCCCCC")
            name = color.get("name", "")
            ax.add_patch(plt.Rectangle((i, 0), 1, 1, color=hex_code))
            label = f"{name}\n{hex_code}" if name else hex_code
            # 밝은 색 배경엔 검정 글씨, 어두운 색 배경엔 흰 글씨
            text_color = "black" if is_light_color(hex_code) else "white"
            ax.text(i + 0.5, 0.5, label, ha="center", va="center",
                     fontsize=10, color=text_color, weight="bold")

        ax.set_xlim(0, n)
        ax.set_ylim(0, 1)
        ax.axis("off")
        ax.set_title("Brand Color Palette", fontsize=13, weight="bold", pad=15)

        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, file_name)
        plt.savefig(file_path, dpi=150, bbox_inches="tight")
        plt.close(fig)

        return file_path

    except Exception as e:
        print(f"      - [컬러 팔레트 이미지 저장 실패] {e}")
        return None


def is_light_color(hex_code: str) -> bool:
    """
    HEX 색상의 밝기를 계산해 밝은 색인지 판단한다 (텍스트 색상 자동 결정용).
    palette_visualizer.py뿐 아니라 image_generator.py의 플레이스홀더 로고 생성에서도
    동일한 로직을 재사용하기 위해 공개(public) 함수로 둔다.
    """
    try:
        hex_code = hex_code.lstrip("#")
        r, g, b = int(hex_code[0:2], 16), int(hex_code[2:4], 16), int(hex_code[4:6], 16)
        brightness = (r * 299 + g * 587 + b * 114) / 1000
        return brightness > 150
    except Exception:
        return True