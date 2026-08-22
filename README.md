# AI 브랜드 아이덴티티 생성기 — 프로젝트 완료 문서

> 브랜드 브리프(업종·타겟·키워드 등) 하나만 입력하면, LLM API와 이미지 생성 API를 조합하여
> **브랜드 네이밍 · 슬로건 · 브랜드 스토리 · 컬러 팔레트 · 로고 시안**까지 자동으로 생성하고
> 파일로 저장해주는 CLI 기반 Python 프로그램.


---

## 목차

1. [프로젝트 배경 및 기획 의도](#1-프로젝트-배경-및-기획-의도)
2. [과제 목표와 달성 내용](#2-과제-목표와-달성-내용)
3. [요구사항 정의](#3-요구사항-정의)
   - 3.1 [최종 결과물](#31-최종-결과물)
   - 3.2 [기능 요구사항 상세](#32-기능-요구사항-상세)
4. [시스템 설계](#4-시스템-설계)
   - 4.1 [전체 파이프라인](#41-전체-파이프라인)
   - 4.2 [기술 스택과 선정 이유](#42-기술-스택과-선정-이유)
   - 4.3 [입력 스펙 — 브랜드 브리프](#43-입력-스펙--브랜드-브리프)
   - 4.4 [출력 스펙 — 결과 파일](#44-출력-스펙--결과-파일)
5. [프로젝트 파일 구조](#5-프로젝트-파일-구조)
6. [모듈별 상세 설계](#6-모듈별-상세-설계)
7. [핵심 설계 원칙](#7-핵심-설계-원칙)
8. [에러 처리 가이드](#8-에러-처리-가이드)
9. [개발 환경 설정 (초보자용)](#9-개발-환경-설정-초보자용)
10. [Git 사용법 및 실전 트러블슈팅](#10-git-사용법-및-실전-트러블슈팅)
11. [실행 방법 및 결과 예시](#11-실행-방법-및-결과-예시)
12. [알려진 이슈 및 대응 기록](#12-알려진-이슈-및-대응-기록)
13. [구현 범위 및 향후 확장 아이디어](#13-구현-범위-및-향후-확장-아이디어)
14. [요구사항 대비 구현 체크리스트](#14-요구사항-대비-구현-체크리스트)

---

## 1. 프로젝트 배경 및 기획 의도

브랜드 디자인 외주비가 수백만 원에서 시작하는 이유가 있습니다. 네이밍, 슬로건, 컬러, 로고까지
하나하나가 전문 영역의 작업이기 때문입니다. 브랜드 디자인은 네이밍 · 슬로건 · 스토리 · 컬러 ·
로고 등 다양한 요소를 종합적으로 기획해야 하는 작업이며, 상당한 시간과 전문성을 요구합니다.

**이 프로젝트의 핵심 아이디어**는 이러한 작업을 **브리프(brief) 하나로 자동화**하는 것입니다.

- 사용자는 업종 / 타겟 / 키워드 등 간단한 정보만 JSON 파일로 준비한다.
- **LLM API**가 이 정보를 바탕으로 네이밍 · 슬로건 · 스토리 · 컬러 팔레트를 텍스트로 생성한다.
- **이미지 생성 API**가 텍스트 결과(브랜드명, 메인 컬러)를 참고해 로고 시안을 그려낸다.
- 모든 결과물은 JSON과 PNG 형태로 폴더에 정리되어 저장된다.

이 과정에서 실무에 가까운 두 가지 기술 조합을 경험하는 것이 이 프로젝트의 진짜 목적입니다.

1. **멀티모달 파이프라인 설계** — 텍스트 생성 API와 이미지 생성 API를 순차적으로 연결하고,
   앞 단계의 결과(브랜드명, 컬러)를 다음 단계(로고 프롬프트)의 입력으로 재사용하는 구조
2. **부분 실패를 허용하는 견고한 파이프라인** — 7번의 API 호출 중 일부가 실패해도 프로그램
   전체가 멈추지 않고, 성공한 결과만이라도 안전하게 저장되는 구조

## 2. 과제 목표와 달성 내용

이 과제를 완료하면 아래 4가지를 스스로 설명할 수 있는 것이 목표였습니다. 각 목표가 실제 코드의
어느 부분에서 어떻게 충족되었는지 정리했습니다.

| # | 과제 목표 | 이 프로젝트에서의 달성 내용 |
|---|---|---|
| 1 | 브랜드 브리프를 입력받아 AI로 브랜드 요소를 생성하는 파이프라인을 설명할 수 있다 | `main.py`가 `brief_loader → text_generator(4단계) → palette_visualizer → image_generator → result_saver` 순서로 전체 흐름을 오케스트레이션. 각 단계는 독립된 모듈 함수로 분리되어 있어 흐름을 코드만 읽어도 추적 가능 |
| 2 | LLM API와 이미지 생성 API를 조합하여 텍스트+이미지 결과물을 생성하는 방법을 설명할 수 있다 | `text_generator.py`가 OpenAI `gpt-4o-mini`로 JSON 구조화 응답을 생성하고, 그 결과(브랜드명 · 메인 컬러)를 `image_generator.py`가 받아 `gpt-image-1` 프롬프트에 그대로 삽입 — 텍스트 결과가 이미지 프롬프트의 재료가 되는 실제 멀티모달 연계 구조 |
| 3 | 생성된 컬러 팔레트를 시각화하여 이미지로 저장하는 방법을 설명할 수 있다 | `palette_visualizer.py`가 matplotlib `Rectangle`로 색상 블록을 그리고, 배경 밝기를 계산해 텍스트 색을 자동으로 흑/백 전환하는 로직까지 포함 (§6 참고) |
| 4 | API 호출 시 발생할 수 있는 오류 상황과 대응 방법을 설명할 수 있다 | [§8 에러 처리 가이드](#8-에러-처리-가이드) 표에 10가지 오류 유형과 실제 코드 대응을 정리. 개발 과정에서 실제로 겪은 오류(§12)까지 포함 |

## 3. 요구사항 정의

### 3.1 최종 결과물

다음 기능이 정상 동작하는 CLI 기반 Python 프로그램 1개.

1. **브랜드 브리프 입력** — JSON 파일로 브랜드 정보(업종, 타겟, 키워드, 톤앤매너 등)를 입력받는다.
2. **AI 기반 브랜드 요소 생성**
   - 브랜드 네이밍 후보 3~5개와 각각의 의미
   - 슬로건/태그라인 3개
   - 브랜드 스토리(탄생 배경, 철학)
   - 브랜드에 어울리는 컬러 팔레트(메인/서브 컬러)
3. **AI 기반 로고 시안 생성** — 이미지 생성 API로 로고 시안 2~3개를 PNG 파일로 저장
4. **결과 저장**
   - 모든 텍스트 결과를 JSON 파일로 저장 (`brand_result.json`)
   - 컬러 팔레트를 시각화하여 PNG 이미지로 저장 (`color_palette.png`)
   - 로고 시안을 PNG 이미지로 저장 (`logo_01.png` ~ `logo_03.png`)

### 3.2 기능 요구사항 상세

| # | 항목 | 상세 내용 | 구현 위치 |
|---|---|---|---|
| 1 | 사용자 입력 | `print`/`input`으로 대화형 입력. 필수: 브리프 파일 경로 / 선택: 출력 폴더 경로(기본값 `./output`) | `main.py: get_user_input()` |
| 2 | 브랜드 브리프 입력 | JSON 파일로 입력. 필수 필드: `industry`, `target`, `keywords` / 선택 필드: `tone`, `competitors`, `notes` | `modules/brief_loader.py` |
| 3 | 브랜드 네이밍 생성 | LLM API로 브랜드명 후보 3~5개 + 15자 이내 의미 설명 생성 | `modules/text_generator.py: generate_naming()` |
| 4 | 슬로건 생성 | LLM API로 톤앤매너에 맞는 슬로건/태그라인 3개 생성 | `modules/text_generator.py: generate_slogans()` |
| 5 | 브랜드 스토리 생성 | LLM API로 탄생 배경/철학/비전을 포함한 300자 내외 스토리 생성 | `modules/text_generator.py: generate_story()` |
| 6 | 컬러 팔레트 생성 | LLM API로 메인 컬러 1개 + 서브 컬러 2~3개(HEX) 추천, matplotlib으로 시각화하여 PNG 저장 | `modules/text_generator.py: generate_color_palette()`, `modules/palette_visualizer.py` |
| 7 | 로고 시안 생성 | 이미지 생성 API(`gpt-image-1`)로 로고 시안 3개 생성 후 PNG 저장 | `modules/image_generator.py` |
| 8 | 결과 저장 | 텍스트 결과는 `brand_result.json`, 이미지는 개별 PNG 파일로 출력 폴더에 저장 | `modules/result_saver.py` |
| 9 | 에러 처리 | API 호출 실패 시 에러 메시지 출력 후 다음 단계 계속 진행 / API 키 오류 시 명확한 안내 메시지 출력 | `modules/config.py`, 각 생성 모듈의 `try/except` |
| 10 | API 키 관리 | API 키를 코드에 직접 작성하지 않고 `.env` 파일(환경변수)에서 읽어옴 | `modules/config.py`, `.env.example` |

## 4. 시스템 설계

### 4.1 전체 파이프라인

```
[사용자 입력]
  브리프 파일 경로 / 출력 폴더 경로
        ↓
[브리프 로드 & 검증]  brief_loader.py
  JSON 파싱, 필수 필드(industry/target/keywords) 확인
        ↓
┌─────────────────────────────────────────────┐
│  텍스트 생성 (OpenAI gpt-4o-mini, 4회 호출)   │  text_generator.py
│  [1/5] 네이밍  → [2/5] 슬로건                 │
│  → [3/5] 스토리 → [4/5] 컬러 팔레트           │
│  (단계별 개별 try-except: 하나 실패해도 계속) │
└─────────────────────┬─────────────────────────┘
                      ↓
[컬러 팔레트 시각화]  palette_visualizer.py
  matplotlib → color_palette.png 저장
                      ↓
┌─────────────────────────────────────────────┐
│  로고 이미지 생성 (OpenAI gpt-image-1, 3회 호출)│ image_generator.py
│  [5/5] 네이밍 결과 + 메인 컬러를 프롬프트에 반영 │
│  (개별 try-except: 실패한 장만 건너뛰고 계속) │
└─────────────────────┬─────────────────────────┘
                      ↓
[결과 저장]  result_saver.py
  brand_result.json + color_palette.png + logo_01~03.png
```

**왜 이 순서인가**

| 설계 결정 | 이유 |
|---|---|
| 브리프 검증을 가장 먼저 | 잘못된 입력으로 인한 불필요한 API 비용 낭비 방지 |
| 텍스트 4단계를 이미지보다 먼저 | 이미지 생성이 텍스트보다 느리고 비용이 높음. 또한 로고 프롬프트가 네이밍/컬러 결과를 참조하므로 순서상 텍스트가 먼저 끝나야 함 |
| 각 단계를 개별 `try-except`로 분리 | 하나의 API 호출 실패가 전체 파이프라인을 중단시키지 않도록 함 (§7 참고) |
| JSON 저장을 맨 마지막에 | 중간에 일부 단계가 실패해도, 그때까지 성공한 결과만이라도 최종 저장 가능 |

### 4.2 기술 스택과 선정 이유

| 구분 | 선택 | 이유 |
|---|---|---|
| 텍스트 생성 API | OpenAI `gpt-4o-mini` | 저비용으로 빠르게 JSON 구조화 응답(`response_format={"type": "json_object"}`)을 안정적으로 받을 수 있음 |
| 이미지 생성 API | OpenAI `gpt-image-1` | 기존 `dall-e-3`는 2026년 5월 12일 OpenAI에서 완전히 폐지되어 더 이상 호출이 불가능함. 후속 모델인 `gpt-image-1`을 사용 (자세한 내용 §12) |
| 컬러 시각화 | matplotlib | 요구사항에 명시된 라이브러리. `Rectangle` 패치로 색상 블록을 직접 그려 세밀한 커스터마이징(라벨, 텍스트 색 자동 대비 등) 가능 |
| 환경변수 관리 | python-dotenv | `.env` 파일을 코드 수정 없이 읽어와 API 키를 코드에서 완전히 분리 |
| HTTP 요청 | requests | 이미지 생성 API가 URL 방식으로 응답할 경우 다운로드용 (b64_json 미제공 시 대비) |

**하나의 API 키로 충분한 이유**: OpenAI는 텍스트(GPT)와 이미지(gpt-image-1) 모두 동일한
`OPENAI_API_KEY` 하나로 호출 가능합니다. 이 프로젝트가 `.env`에 키를 1개만 요구하는 것은
이 때문입니다.

### 4.3 입력 스펙 — 브랜드 브리프

| 필드 | 필수 | 타입 | 설명 | 예시 |
|---|---|---|---|---|
| `industry` | ✅ | string | 업종 | `"스페셜티 커피 전문점"` |
| `target` | ✅ | string | 타겟 고객 | `"20~30대 직장인, 커피 애호가"` |
| `keywords` | ✅ | array 또는 콤마 구분 string | 핵심 키워드 | `["신선함", "정직한 원두"]` |
| `tone` | ⬜ | string | 톤앤매너 | `"친근하지만 전문적인"` |
| `competitors` | ⬜ | string/array | 경쟁사 (프롬프트 컨텍스트로만 참고됨, §13 참고) | `"블루보틀, 프릳츠"` |
| `notes` | ⬜ | string | 추가 요청사항 | `"과하지 않은 편안한 느낌"` |

`brief_loader.py`는 `keywords`가 문자열로 들어와도 콤마 기준으로 자동 분리하며, 선택 필드가
없으면 빈 문자열로 기본값을 채워 이후 로직에서 `KeyError` 없이 안전하게 동작하도록 합니다.

### 4.4 출력 스펙 — 결과 파일

```
output/
├── brand_result.json     # 모든 텍스트 결과 + 생성 파일 목록
├── color_palette.png     # 컬러 팔레트 시각화
├── logo_01.png            # 로고 시안 1
├── logo_02.png            # 로고 시안 2
└── logo_03.png            # 로고 시안 3
```

`brand_result.json` 구조 (`result_saver.py` 기준):

```json
{
  "generated_at": "2026-08-14T06:24:00",
  "brief": { "...원본 브리프..." },
  "naming": [
    {"name": "골목커피 (Alley Coffee)", "meaning": "동네 골목의 즐거움"}
  ],
  "slogans": ["당신의 하루를 따뜻하게, 정직한 원두로."],
  "story": "브랜드 스토리 전체 텍스트...",
  "colors": {
    "main_color": {"hex": "#4E9F3D", "name": "Fresh Green", "reason": "..."},
    "sub_colors": [{"hex": "#D1B18A", "name": "Beige", "reason": "..."}]
  },
  "generated_files": {
    "color_palette_image": "color_palette.png",
    "logo_images": ["logo_01.png", "logo_02.png", "logo_03.png"]
  }
}
```

## 5. 프로젝트 파일 구조

```
brand-ai-generator/
├── main.py                       # CLI 진입점 (전체 실행 흐름 제어)
├── requirements.txt               # 설치가 필요한 패키지 목록
├── .env.example                   # API 키 입력 예시 파일 (실제 키 X)
├── .env                           # 실제 API 키 (직접 생성, Git 추적 제외)
├── .gitignore                     # Git이 추적하지 않을 파일/폴더 목록
├── .gitattributes                 # 줄바꿈 문자(LF/CRLF) 통일 설정
├── sample_brief.json              # 테스트용 샘플 브랜드 브리프
├── README.md                      # 프로젝트 문서 (현재 파일)
├── modules/                       # 기능별 모듈 패키지
│   ├── __init__.py
│   ├── config.py                  # API 키 로딩 및 검증
│   ├── brief_loader.py            # 브리프 JSON 로딩/검증
│   ├── text_generator.py          # gpt-4o-mini: 네이밍/슬로건/스토리/컬러 생성
│   ├── image_generator.py         # gpt-image-1: 로고 시안 생성
│   ├── palette_visualizer.py      # matplotlib: 컬러 팔레트 시각화
│   └── result_saver.py            # 최종 결과 JSON 저장
└── output/                        # 실행 결과물이 저장되는 폴더 (자동 생성)
    ├── brand_result.json
    ├── color_palette.png
    ├── logo_01.png
    ├── logo_02.png
    └── logo_03.png
```

**왜 이렇게 나눴나** — 단일 책임 원칙에 따라 파일 하나 = 역할 하나로 분리했습니다. 새로운
생성 기능(예: 홍보 문구 생성)을 추가하려면 `text_generator.py`에 함수 하나만 추가하고
`main.py`에서 호출 한 줄만 추가하면 되는 구조입니다.

## 6. 모듈별 상세 설계

### `main.py` — CLI 오케스트레이션

- `get_user_input()`: 브리프 경로(필수, 빈 값이면 재입력 루프)와 출력 폴더(선택, 기본 `./output`)를 입력받습니다.
- `print_naming_result()` 등 4개의 `print_*_result()` 함수: 각 단계의 생성 결과를 [실행 결과 예시]와 동일한 포맷으로 출력합니다. 네이밍 의미 설명은 **15자를 넘으면 자동으로 잘라 `...`을 붙이는 안전장치**가 있습니다 (프롬프트로 15자를 요청하지만, LLM이 이를 넘길 가능성에 대비한 이중 안전망).
- `main()`: 5단계를 순서대로 호출하고, 각 단계 사이에 `[N/5] ... 생성 중...` 헤더를 출력합니다.

### `modules/config.py` — API 키 관리

- `python-dotenv`로 `.env` 파일을 자동 로드합니다 (설치가 안 되어 있어도 예외 처리로 프로그램이 죽지 않음).
- `get_openai_api_key()`: 키가 없으면 `.env` 작성법과 환경변수 직접 설정법을 안내하고 `sys.exit(1)`로 즉시 종료합니다. 키가 있지만 `sk-`로 시작하지 않으면 경고만 출력하고 계속 진행합니다 (실제 유효성은 API 호출 시점에 판별).

### `modules/brief_loader.py` — 브리프 검증

- 파일 존재 여부, JSON 문법, 필수 필드(`industry`/`target`/`keywords`) 3가지를 순서대로 검사합니다.
- `keywords`가 배열이 아니라 문자열로 들어와도(`"신선함, 정직함"`) 자동으로 콤마 분리해 배열로 변환합니다 — 사용자가 JSON 문법에 서툴러도 유연하게 동작하도록 한 설계입니다.

### `modules/text_generator.py` — 텍스트 브랜드 요소 생성

4개의 생성 함수(`generate_naming`, `generate_slogans`, `generate_story`, `generate_color_palette`)가
모두 공통 헬퍼 `_call_json()`을 통해 `response_format={"type": "json_object"}` 옵션으로
OpenAI Chat Completions API를 호출합니다. 이는 [8.1 LLM에서 구조화된 데이터 받기] 문제에 대한
"방법 ②"에 해당하며, LLM이 설명 문장을 덧붙이지 않고 순수 JSON만 반환하도록 강제합니다.

**프롬프트 설계 원칙** (실제 코드에 적용된 5가지):

| 원칙 | 적용 예시 |
|---|---|
| 역할 부여 | "당신은 전문 브랜드 네이밍 컨설턴트입니다" |
| 명확한 지시 | "브랜드명 후보를 3~5개 제안해주세요" |
| 컨텍스트 제공 | `_build_brief_context()`가 industry/target/keywords/tone/competitors/notes를 프롬프트에 포함 |
| 출력 형식 지정 | `{"names": [{"name": "...", "meaning": "..."}]}` 형태를 프롬프트에 명시 |
| 제약 조건 | 네이밍 의미는 "15자 이내", 스토리는 "300자 내외", 컬러는 "반드시 #RRGGBB 형식" |

`generate_naming()`은 특히 의미 설명 길이 제약이 까다로워, "완전한 문장이 아니라 명사구로
끝낼 것", "말줄임표/마침표 금지"까지 명시해 모델이 15자 제약을 지키도록 강하게 유도합니다.

모든 함수는 실패 시 예외를 상위로 던지지 않고 `_handle_api_error()`로 로그만 남긴 뒤 `None`을
반환해, `main.py`가 다음 단계로 계속 진행할 수 있게 합니다.

### `modules/image_generator.py` — 로고 시안 생성

- `_build_logo_prompt()`: 네이밍 1순위 결과와 메인 컬러 HEX 코드를 영문 프롬프트에 삽입해
  텍스트 생성 결과가 로고 디자인에 반영되도록 합니다.
- `generate_logos()`: `LOGO_COUNT`(기본 3)만큼 반복 호출하며, 파일명은 `logo_01.png`처럼
  2자리 zero-padding으로 저장합니다.
- 이미지 API 응답은 SDK/모델 버전에 따라 `b64_json` 또는 `url` 둘 중 하나로 올 수 있어, 두
  경우를 모두 처리하도록 방어적으로 작성되어 있습니다 (`response_format` 파라미터는 일부
  모델/SDK 조합에서 지원되지 않으므로 아예 넘기지 않음 — §12 참고).
- 인증 오류(`AuthenticationError`)는 이후 로고를 더 시도해봤자 계속 실패할 것이 확실하므로
  루프를 즉시 `break`하지만, 요청 한도 초과나 네트워크 오류 등은 `continue`로 다음 로고를
  계속 시도합니다. 이 구분이 불필요한 API 낭비를 막습니다.

### `modules/palette_visualizer.py` — 컬러 팔레트 시각화

- `_set_korean_font()`: OS별 한글 폰트(Windows `Malgun Gothic`, macOS `AppleGothic`,
  Linux `NanumGothic`/`Noto Sans CJK KR`)를 자동 탐색해 matplotlib에 등록합니다. 이 처리가
  없으면 한글 라벨이 네모(□)로 깨져 보입니다.
- `save_palette_image()`: 메인 컬러 + 서브 컬러를 `Rectangle`로 그리고, `_is_light_color()`로
  각 색상의 밝기(YIQ 공식 기반)를 계산해 텍스트 색을 흑/백으로 자동 전환합니다 — 밝은 색
  배경에 흰 글씨, 어두운 색 배경에 검은 글씨가 겹쳐 안 보이는 문제를 방지합니다.

### `modules/result_saver.py` — 최종 결과 저장

- 네이밍/슬로건/스토리/컬러 중 실패한 항목이 있어도 `None`을 빈 값(`[]`, `""`, `{}`)으로
  치환해 JSON 저장이 항상 성공하도록 합니다. 이것이 "부분 실패 허용 파이프라인"의 마지막
  안전장치입니다.

## 7. 핵심 설계 원칙

### 부분 실패를 허용하는 파이프라인

```python
# 나쁜 예 — 하나 실패하면 전부 날아감
try:
    naming = generate_naming()
    slogans = generate_slogans()
    story = generate_story()
except Exception as e:
    print(f"실패: {e}")

# 이 프로젝트의 방식 — 각 단계를 독립적으로 처리
naming = generate_naming(client, brief)     # 내부에서 실패해도 None 반환
slogans = generate_slogans(client, brief)   # naming 실패와 무관하게 계속 실행
story = generate_story(client, brief)
colors = generate_color_palette(client, brief)
# → 4개 중 몇 개가 실패하든, 성공한 결과만으로 brand_result.json이 저장됨
```

### 이중 안전망(dual safety net) 패턴

이 프로젝트는 "AI 응답이 제약을 어길 가능성"에 대해 프롬프트 지시 + 코드 검증의 2단계 방어를
사용합니다. 대표적으로 네이밍 의미 설명의 15자 제한이 있습니다.

1. **1차 방어 (프롬프트)**: `text_generator.py`의 `generate_naming()` 프롬프트에서 "15자를
   넘지 않을 것"을 여러 번 강조
2. **2차 방어 (코드)**: `main.py`의 `print_naming_result()`가 15자를 초과하면 강제로 잘라
   `...`을 붙임

이렇게 하면 LLM이 지시를 완벽히 지키지 못하더라도 최종 출력은 항상 요구사항을 만족합니다.

### 모델/SDK 버전 변화에 대한 방어적 설계

`image_generator.py`는 `response_format` 파라미터를 아예 사용하지 않고, 응답에 `b64_json`이
있으면 디코딩하고 없으면 `url`을 다운로드하는 방식으로 작성되어 있습니다. 이는 실제로 개발
중 `dall-e-3` 모델 폐지와 파라미터 미지원 오류를 겪은 뒤 반영한 설계입니다 (§12).

## 8. 에러 처리 가이드

과제 목표 4번(*API 호출 시 발생할 수 있는 오류 상황과 대응 방법*)에 해당하는 내용입니다.
이 프로그램은 **한 단계가 실패해도 전체가 멈추지 않고, 실패한 단계만 건너뛰고 계속 진행**하는
것을 기본 원칙으로 합니다.

| 오류 상황 | 발생 원인 | 프로그램의 대응 | 사용자가 해야 할 일 |
|---|---|---|---|
| **API 키 누락** (`OPENAI_API_KEY` 없음) | `.env` 파일을 만들지 않았거나 환경변수 미설정 | 프로그램 시작 직후 감지하여 안내 메시지 출력 후 **즉시 종료** (`sys.exit(1)`) | `.env` 파일에 `OPENAI_API_KEY=sk-...` 추가 |
| **API 키 인증 실패** (`AuthenticationError`) | 키 값이 잘못되었거나 만료/폐기됨 | 해당 단계에서 에러 메시지 출력 후 **해당 단계만 건너뛰고 다음 단계 진행** (로고는 이후 시도 전체를 중단) | OpenAI 대시보드에서 키 상태 확인, 새 키 발급 후 `.env` 갱신 |
| **API 요청 한도 초과** (`RateLimitError`) | 짧은 시간에 너무 많은 요청, 또는 사용량/결제 한도 초과 | 에러 메시지 출력 후 해당 단계를 건너뛰고 계속 진행 | 잠시 후 재실행, 또는 OpenAI 결제 정보/한도 확인 |
| **네트워크 연결 오류** (`APIConnectionError`) | 인터넷 연결 불안정, 방화벽/프록시 차단 | 에러 메시지 출력 후 해당 단계를 건너뛰고 계속 진행 | 네트워크 상태 확인 후 재실행 |
| **OpenAI 서버 오류** (`APIError`, 4xx/5xx) | 모델 폐지, 파라미터 미지원, 서버 일시 장애 등 | 에러 메시지 출력 후 해당 단계를 건너뛰고 계속 진행 | 오류 메시지의 `code`/`message` 확인 (§12), 잠시 후 재시도 |
| **JSON 파싱 실패** (`JSONDecodeError`) | LLM 응답이 JSON 형식이 아니거나 형식이 깨짐 | 에러 메시지 출력 후 해당 단계 결과를 빈 값으로 처리, 다음 단계 진행 | 재실행 시 대부분 정상 생성됨 (모델 응답의 변동성) |
| **브리프 파일 없음/경로 오류** | 사용자가 잘못된 경로 입력 | `[브리프 오류]` 메시지 출력 후 프로그램 종료 | 올바른 파일 경로 재입력 |
| **브리프 JSON 형식 오류** | JSON 문법 오류(콤마 누락 등) | 오류 위치와 함께 메시지 출력 후 프로그램 종료 | JSON 문법 검사 후 재실행 (예: jsonlint.com) |
| **브리프 필수 필드 누락** | `industry`/`target`/`keywords` 중 하나라도 없음 | 누락된 필드명을 출력하고 프로그램 종료 | 브리프 파일에 필수 필드 추가 후 재실행 |
| **로고 이미지 저장 실패** (디스크/권한 문제) | 출력 폴더 쓰기 권한 없음, 디스크 용량 부족 등 | 에러 메시지 출력 후 해당 로고만 건너뛰고 다음 로고 계속 생성 | 출력 폴더 권한/용량 확인 |

> 설계 원칙: 텍스트 생성(§3.2의 3~6번)과 이미지 생성(7번)은 서로 독립적으로 동작하므로,
> 예를 들어 로고 생성에 전부 실패하더라도 이미 만들어진 네이밍/슬로건/스토리/컬러 결과는
> 정상적으로 `brand_result.json`에 저장됩니다.

## 9. 개발 환경 설정 (초보자용)

Python을 처음 다뤄보는 분도 순서대로 따라 할 수 있도록 단계별로 정리했습니다.

### STEP 1. Python 설치 확인

```bash
python3 --version
# Windows에서는
python --version
```

`Python 3.9` 이상이면 정상입니다. 설치되어 있지 않다면 [python.org](https://www.python.org/downloads/)에서
설치 파일을 내려받아 설치하세요. (Windows는 설치 시 **"Add Python to PATH"** 체크 필수)

### STEP 2. 프로젝트 폴더로 이동

```bash
cd brand-ai-generator
```

### STEP 3. 가상환경(venv) 생성 및 활성화

```bash
python3 -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows (PowerShell)
venv\Scripts\Activate.ps1

# Windows (cmd)
venv\Scripts\activate.bat
```

활성화되면 터미널 프롬프트 앞에 `(venv)`가 표시됩니다.

### STEP 4. 패키지 설치

```bash
pip install -r requirements.txt
```

### STEP 5. API 키 설정

1. [OpenAI API 키 발급 페이지](https://platform.openai.com/api-keys)에서 API 키를 발급받습니다.
   (⚠️ 발급만으로는 부족하고, OpenAI 계정에 **결제 수단이 등록**되어 있어야 실제 호출이 됩니다.
   무료 크레딧이 소진되면 카드 미등록 시 호출이 거부됩니다.)
2. `.env.example`을 복사해서 `.env` 파일을 만듭니다.

```bash
# macOS / Linux
cp .env.example .env
# Windows
copy .env.example .env
```

3. `.env` 파일을 열어 발급받은 키를 입력합니다.

```
OPENAI_API_KEY=sk-발급받은실제키값
```

> ⚠️ `.env` 파일은 `.gitignore`에 등록되어 있어 Git에 커밋되지 않습니다. 절대로 API 키를
> 코드에 직접 작성하거나 GitHub에 올리지 마세요.

### STEP 6. 실행

```bash
python3 main.py
```

### STEP 7. 가상환경 종료 (작업 종료 시)

```bash
deactivate
```

## 10. Git 사용법 및 실전 트러블슈팅

버전 관리를 처음 해보는 분들을 위한 기본 명령어와, **이 프로젝트를 실제로 GitHub에 올리며
겪었던 문제와 해결 과정**을 함께 정리했습니다.

### 기본 명령어

| 단계 | 명령어 | 설명 |
|---|---|---|
| Git 설치 확인 | `git --version` | 없다면 [git-scm.com](https://git-scm.com/)에서 설치 |
| 사용자 정보 최초 설정 | `git config --global user.name "이름"` / `git config --global user.email "이메일"` | 최초 1회만 설정 |
| 저장소 초기화 | `git init` | 프로젝트 폴더를 Git 저장소로 만듦 |
| 변경 사항 확인 | `git status` | 어떤 파일이 추가/수정/삭제되었는지 확인 |
| 스테이징 | `git add .` | 모든 변경 파일을 커밋 대상으로 등록 (`.env`는 제외됨) |
| 커밋 | `git commit -m "커밋 메시지"` | 스테이징된 변경 사항을 저장 |
| 원격 저장소 연결 | `git remote add origin <저장소_URL>` | GitHub와 연결 (최초 1회) |
| 원격 저장소로 업로드 | `git push origin main` | 로컬 커밋을 원격으로 전송 |
| 원격 저장소에서 내려받기 | `git pull origin main` | 원격의 최신 변경 사항을 받아옴 |
| 커밋 로그 확인 | `git log --oneline` | 커밋 이력을 한 줄씩 확인 |

### 처음 GitHub에 업로드하는 전체 흐름

```bash
git init
git add .
git commit -m "Initial commit: 브랜드 AI 생성기 프로젝트"
git branch -M main
git remote add origin https://github.com/사용자명/brand-ai-generator.git
git push -u origin main
```

> 💡 마지막 줄의 `-u` 옵션이 핵심입니다. `-u`(`--set-upstream`)를 붙여 push하면 로컬
> `main`과 원격 `origin/main`이 자동으로 "짝(tracking)"으로 연결되어, 이후에는
> `git pull`, `git push`만 입력해도 자동으로 동기화됩니다.

### 실전에서 겪은 문제와 해결 (원인 → 해결 순)

**1) `git add .` 시 "LF will be replaced by CRLF..." 경고**

- **원인**: Windows(CRLF)와 Git 저장소 기준(LF)의 줄바꿈 문자가 달라서 Git이 자동 변환
  중이라는 **안내일 뿐, 오류가 아님**.
- **해결**: 그냥 무시하고 진행해도 무방. 경고 자체를 없애려면 `.gitattributes`에
  `* text=auto eol=lf`를 추가 (이 프로젝트에 이미 포함됨).

**2) `git push` 시 `! [rejected] main -> main (fetch first)`**

- **원인**: 원격 저장소에 로컬에는 없는 커밋이 있음 (예: GitHub에서 저장소 생성 시
  "Add a README" 옵션을 체크한 경우).
- **해결**: `git pull origin main` 으로 원격 변경 사항을 먼저 받아온 뒤 다시 push.

**3) `git pull` 시 "There is no tracking information for the current branch"**

- **원인**: `git init` + `git remote add`로 시작한 저장소는 `git clone`이나
  `git push -u`와 달리 로컬 브랜치와 원격 브랜치의 tracking 연결이 자동으로 되지 않음.
  (`remote add`는 "원격 주소를 등록"하는 것일 뿐, "브랜치끼리 짝을 맺는 것"은 아님)
- **해결**:
  ```bash
  git branch --set-upstream-to=origin/main main
  git pull
  ```

**4) `git pull` 시 `fatal: refusing to merge unrelated histories`**

- **원인**: 로컬(`git init`으로 새로 시작)과 원격(GitHub에서 자동 커밋 생성)이 히스토리상
  전혀 연결점이 없는 "남남" 상태이기 때문. Git이 실수로 엉뚱한 저장소를 합치는 것을 막기 위해
  기본적으로 거부함.
- **해결**: 의도된 상황임을 명시적으로 알려주면 됨.
  ```bash
  git pull origin main --allow-unrelated-histories
  ```

**5) 병합 중 `CONFLICT (add/add): Merge conflict in README.md`**

- **원인**: 로컬에도 `README.md`, 원격(GitHub 자동 생성)에도 `README.md`가 있어서 같은
  파일이 서로 다른 내용으로 존재 — Git이 어느 쪽을 남길지 판단하지 못함.
- **해결**: 충돌 파일을 열어 `<<<<<<<` / `=======` / `>>>>>>>` 표시 사이에서 남길 내용만
  선택하고 표시를 모두 지운 뒤:
  ```bash
  git add README.md
  git commit -m "Merge: README 충돌 해결"
  git push origin main
  ```

## 11. 실행 방법 및 결과 예시

```bash
# 1) 가상환경 활성화
source venv/bin/activate

# 2) 프로그램 실행
python3 main.py

# 3) 안내에 따라 입력
브리프 파일 경로를 입력하세요: sample_brief.json
출력 폴더 경로를 입력하세요 (엔터 시 ./output):
```

### 실행 결과 예시

```
$ python main.py

    🎨 AI 브랜드 아이덴티티 생성기

    브리프 파일 경로를 입력하세요: sample_brief.json
    출력 폴더 경로를 입력하세요 (엔터 시 ./output):

    [1/5] 브랜드 네이밍 생성 중...
      - 블루밍 (Blooming): 자연에서 피어나는 아름다움
      - 소소담: 소소한 일상에 자연을 담다
      - 어반리프 (Urban Leaf): 도시 속 자연의 싱그러움
    [2/5] 슬로건 생성 중...
      - "일상에 자연을 담다"
      - "피부가 숨쉬는 순간"
      - "자연 그대로, 당신 그대로"
    [3/5] 브랜드 스토리 생성 중...
      - 스토리 생성 완료 (287자)
    [4/5] 컬러 팔레트 생성 중...
      - 메인: #2E7D32 (Forest Green)
      - 서브: #81C784, #E8F5E9
      - 저장: ./output/color_palette.png
    [5/5] 로고 시안 생성 중...
      - 저장: ./output/logo_01.png
      - 저장: ./output/logo_02.png
      - 저장: ./output/logo_03.png

    ✅ 완료! ./output/ 폴더를 확인하세요.
```

> API 호출이 실패하는 단계가 있어도 해당 단계의 실패 메시지만 출력되고 나머지 단계는 계속
> 진행됩니다. 자세한 내용은 [§8 에러 처리 가이드](#8-에러-처리-가이드)를 참고하세요.

실행이 끝나면 `output/` 폴더(또는 직접 지정한 폴더)에 아래 파일들이 생성됩니다.

- `brand_result.json` — 네이밍, 슬로건, 스토리, 컬러 정보, 생성된 파일 목록
- `color_palette.png` — 컬러 팔레트 시각화 이미지
- `logo_01.png`, `logo_02.png`, `logo_03.png` — AI가 생성한 로고 시안

## 12. 알려진 이슈 및 대응 기록

개발 및 실제 사용 과정에서 발견되어 코드에 반영된 이슈들입니다. 같은 문제를 겪을 다른
사용자를 위해 원인과 해결을 기록으로 남깁니다.

| 이슈 | 증상 | 원인 | 조치 |
|---|---|---|---|
| `dall-e-3` 모델 폐지 | `Error code: 400 - The model 'dall-e-3' does not exist` | OpenAI가 2026년 5월 12일부로 `dall-e-3`를 완전히 서비스 종료(retire)함 | `IMAGE_MODEL`을 `gpt-image-1`로 교체 (`modules/image_generator.py`) |
| `response_format` 파라미터 미지원 | `Error code: 400 - Unknown parameter: 'response_format'` | 설치된 SDK/모델 조합이 이미지 생성 API의 `response_format` 파라미터를 받지 않음 | 파라미터를 아예 넘기지 않고, 응답의 `b64_json`/`url` 여부를 코드에서 분기 처리 |
| 네이밍 설명이 너무 길어짐 | 한 줄 출력이 여러 줄로 늘어남 | LLM이 프롬프트의 길이 제약을 완벽히 지키지 않는 경우가 있음 | 프롬프트에 15자 제한을 여러 차례 명시 + `main.py`에 15자 초과 시 자동 절단하는 코드 안전장치 추가 (§7 이중 안전망) |
| 한글이 네모(□)로 깨짐 | matplotlib 팔레트 이미지의 한글 라벨이 깨짐 | matplotlib 기본 폰트가 한글을 지원하지 않음 | `palette_visualizer.py`에 OS별 한글 폰트 자동 탐색/등록 로직 추가 |

## 13. 구현 범위 및 향후 확장 아이디어

현재 구현은 **필수 요구사항(§3) 전체**를 충족하는 것에 집중되어 있습니다. 브리프 스키마에는
보너스 과제와 관련된 필드(`competitors`)가 포함되어 있고 프롬프트 컨텍스트로 전달되어 생성
결과에 은연중 영향을 주지만, 아래 두 가지는 **별도의 전용 기능으로는 아직 구현되어 있지
않습니다.**

| 아이디어 | 현재 상태 | 구현 방향 |
|---|---|---|
| 경쟁사 분석 기능 | `competitors` 필드는 프롬프트 컨텍스트에만 포함됨. 별도의 차별화 포인트 출력 없음 | `text_generator.py`에 `generate_competitor_analysis()` 함수를 추가하고, `brief.get("competitors")`가 있을 때만 `main.py`에서 조건부 호출 (`[6/6]` 단계로 확장) |
| 다국어 네이밍 (한/영 분리) | 현재는 `name` 필드 하나에 `"한글명 (English Name)"` 형태로 선택적으로 포함 | JSON 스키마를 `{"name_ko": "...", "name_en": "...", "meaning": "..."}`로 변경하고 프롬프트/출력 포맷팅 함수를 함께 수정 |
| API 재시도(retry) 로직 | 현재는 실패 시 해당 단계를 건너뛰기만 함 (재시도 없음) | `tenacity` 라이브러리로 지수 백오프(exponential backoff) 재시도 래퍼를 `_call_json()`에 적용 |
| 비용 계산/토큰 사용량 출력 | 미구현 | `response.usage` 필드를 활용해 실행 후 예상 비용을 요약 출력 |

## 14. 요구사항 대비 구현 체크리스트

- [x] JSON 브리프 파일 로드 & 파싱
- [x] 필수 필드(industry, target, keywords) 검증
- [x] LLM API로 네이밍 3~5개 생성
- [x] LLM API로 슬로건 3개 생성
- [x] LLM API로 브랜드 스토리 300자 내외 생성
- [x] LLM API로 컬러 팔레트 생성 (메인 + 서브, HEX)
- [x] matplotlib으로 팔레트 PNG 저장 (한글 폰트 자동 처리 포함)
- [x] 이미지 API로 로고 3개 PNG 저장
- [x] 모든 텍스트 결과를 `brand_result.json`으로 저장
- [x] 각 API 호출을 개별 try-except로 감쌈 (부분 실패 허용)
- [x] 환경변수(`.env`)로 API 키 관리, 코드에 하드코딩 없음
- [x] API 키 미설정 시 명확한 에러 메시지 및 종료
- [ ] 경쟁사 차별화 분석 기능 (보너스, §13 참고)
- [ ] 다국어 네이밍 전용 필드 분리 (보너스, §13 참고)
- [ ] 재시도(retry) 로직 (선택 구현, §13 참고)