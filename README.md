# AI 브랜드 아이덴티티 생성기 — 프로젝트 완료 문서

> 브랜드 브리프(업종·타겟·키워드 등) 하나만 입력하면, LLM API와 이미지 생성 API를 조합하여
> **브랜드 네이밍 · 슬로건 · 브랜드 스토리 · 컬러 팔레트 · 로고 시안**까지 자동으로 생성하고
> 파일로 저장해주는 CLI 기반 Python 프로그램.


---


## 📌 프로젝트 배경 및 기획 의도

브랜드 디자인 외주비가 수백만 원에서 시작하는 이유가 있습니다. 네이밍, 슬로건, 컬러, 로고까지
하나하나가 전문 영역의 작업이기 때문입니다.   
브랜드 디자인은 네이밍 · 슬로건 · 스토리 · 컬러 · 로고 등 다양한 요소를 종합적으로 기획해야 하는 작업이며, 상당한 시간과 전문성을 요구합니다.

✅ **이 프로젝트의 핵심 아이디어**는 이러한 작업을 **브리프(brief) 하나로 자동화**하는 것입니다.

- 사용자는 업종 / 타겟 / 키워드 등 간단한 정보만 JSON 파일로 준비한다.
- **LLM API**가 이 정보를 바탕으로 네이밍 · 슬로건 · 스토리 · 컬러 팔레트를 텍스트로 생성한다.
- **이미지 생성 API**가 텍스트 결과(브랜드명, 메인 컬러)를 참고해 로고 시안을 그려낸다.
- 모든 결과물은 JSON과 PNG 형태로 폴더에 정리되어 저장된다.

이 과정에서 실무에 가까운 두 가지 기술 조합을 경험하는 것이 이 프로젝트의 진짜 목적입니다.

✅ **멀티모달 파이프라인 설계**   
  -  텍스트 생성 API와 이미지 생성 API를 순차적으로 연결하고,  
  -  앞 단계의 결과(브랜드명, 컬러)를 다음 단계(로고 프롬프트)의 입력으로 재사용하는 구조
    
✅  **부분 실패를 허용하는 견고한 파이프라인**    
  -  7번의 API 호출 중 일부가 실패해도 프로그램  
  -  전체가 멈추지 않고, 성공한 결과만이라도 안전하게 저장되는 구조  

## 📌 과제 목표와 달성 내용

이 과제를 완료하면 아래 4가지를 스스로 설명할 수 있는 것이 목표였습니다.   
각 목표가 실제 코드의 어느 부분에서 어떻게 충족되었는지 정리했습니다.  

| # | 과제 목표 | 이 프로젝트에서의 달성 내용 |
|---|---|---|
| 1 | 브랜드 브리프를 입력받아 AI로 브랜드 요소를 생성하는 파이프라인을 설명할 수 있다 | `main.py`가 `brief_loader → text_generator(4단계) → palette_visualizer → image_generator → result_saver` 순서로 전체 흐름을 오케스트레이션. 각 단계는 독립된 모듈 함수로 분리되어 있어 흐름을 코드만 읽어도 추적 가능 |
| 2 | LLM API와 이미지 생성 API를 조합하여 텍스트+이미지 결과물을 생성하는 방법을 설명할 수 있다 | `text_generator.py`가 OpenAI `gpt-4o-mini`로 JSON 구조화 응답을 생성하고, 그 결과(브랜드명 · 메인 컬러)를 `image_generator.py`가 받아 `gpt-image-1` 프롬프트에 그대로 삽입 — 텍스트 결과가 이미지 프롬프트의 재료가 되는 실제 멀티모달 연계 구조 |
| 3 | 생성된 컬러 팔레트를 시각화하여 이미지로 저장하는 방법을 설명할 수 있다 | `palette_visualizer.py`가 matplotlib `Rectangle`로 색상 블록을 그리고, 배경 밝기를 계산해 텍스트 색을 자동으로 흑/백 전환하는 로직까지 포함  |
| 4 | API 호출 시 발생할 수 있는 오류 상황과 대응 방법을 설명할 수 있다 | [에러 처리 가이드](#에러-처리-가이드) 표에 10가지 오류 유형과 실제 코드 대응을 정리. 개발 과정에서 실제로 겪은 오류까지 포함 |



## 📌 팀 프로젝트 역할 분담 

### ✅ 역할 분담표

| 역할 | 담당 파일 | 주요 작업 | 필요 역량 |
|---|---|---|---|
| **A(민미경). / 파이프라인 통합** | `main.py`, `modules/config.py`, `modules/brief_loader.py` | CLI 입출력 흐름, API 키 관리, 브리프 검증, 전체 모듈 연결·통합 테스트, 최종 실행 확인 | 프로젝트 구조 이해, 통합 디버깅 |
| **B(김재민). 텍스트 생성① (네이밍·슬로건)** | `text_generator.py` 中 `generate_naming()`, `generate_slogans()` | 프롬프트 엔지니어링, JSON 스키마 설계, 15자 제약 등 출력 형식 튜닝 | 프롬프트 작성 감각 |
| **C(손애희). 텍스트 생성② (스토리·컬러) + 시각화** | `text_generator.py` 中 `generate_story()`, `generate_color_palette()`, `palette_visualizer.py` | 스토리 프롬프트, 컬러 팔레트 추천 프롬프트, matplotlib 시각화(한글 폰트 처리 포함) | 프롬프트 + matplotlib |
| **D(이미영). 이미지 생성** | `image_generator.py` | 로고 프롬프트 설계, `gpt-image-1` 호출, 에러 처리(인증/네트워크/한도) | API 에러 핸들링 |
| **E(류정민). 결과 저장 · 문서 · QA** | `result_saver.py`, `README.md`, 테스트용 브리프 | JSON 저장 로직, README 작성/관리, 다양한 브리프로 테스트, 발표자료 | 문서화, 꼼꼼함 |

> `text_generator.py`는 함수가 4개라 B/C 둘이 나눠 맡음. 같은 파일이므로 **병합 전
> 서로 diff를 꼭 공유**할 것.

### ✅ Git 브랜치 전략

```
main (보호 브랜치, 항상 동작하는 상태 유지)
 ├─ feature/pipeline      (A)
 ├─ feature/naming-slogan (B)
 ├─ feature/story-palette (C)
 ├─ feature/logo          (D)
 └─ feature/result-doc    (E)
```

> 각자 브랜치에서 작업 → PR(Pull Request) → 최소 1명 리뷰 후 `main`에 merge하는 방식.


## 📌 요구사항 정의

### ✅ 최종 결과물

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

### ✅ 기능요구사항 상세

| # | 항목 | 상세 내용 | 구현 위치 |
|---|---|---|---|
| 1 | 사용자 입력 | `print`/`input`으로 대화형 입력. 필수: 브리프 파일 경로 / 선택: 출력 폴더 경로(기본값 `./output`) | `main.py: get_user_input()` |
| 2 | 브랜드 브리프 입력 | JSON 파일로 입력. 필수 필드: `industry`, `target`, `keywords` / 선택 필드: `tone`, `competitors`, `notes` | `modules/brief_loader.py` |
| 3 | 브랜드 네이밍 생성 | LLM API로 브랜드명 후보 3~5개 + 15자 이내 의미 설명 생성 | `modules/text_generator.py: generate_naming()` |
| 4 | 슬로건 생성 | LLM API로 톤앤매너에 맞는 슬로건/태그라인 3개 생성 | `modules/text_generator.py: generate_slogans()` |
| 5 | 브랜드 스토리 생성 | LLM API로 탄생 배경/철학/비전을 포함한 300자 내외 스토리 생성 | `modules/text_generator.py: generate_story()` |
| 6 | 컬러 팔레트 생성 | LLM API로 메인 컬러 1개 + 서브 컬러 2~3개(HEX) 추천, matplotlib으로 시각화하여 PNG 저장 | `modules/text_generator.py: generate_color_palette()`, `modules/palette_visualizer.py` |
| 7 | 로고 시안 생성 | 이미지 생성 API(`gpt-image-1`)로 로고 시안 3개 생성 후 PNG 저장. 일시적 오류는 재시도, 그래도 실패하면 플레이스홀더 이미지로 대체해 항상 2~3개를 확보 | `modules/image_generator.py` |
| 8 | 결과 저장 | 텍스트 결과는 `brand_result.json`, 이미지는 개별 PNG 파일로 출력 폴더에 저장. 단계별 실패 기록도 `errors` 필드에 함께 저장 | `modules/result_saver.py` |
| 9 | 에러 처리 | API 호출 실패 시 에러 메시지 출력 후 다음 단계 계속 진행 / API 키 오류 시 명확한 안내 메시지 출력 / 실패 정보를 `errors` 리스트로 수집해 결과 JSON에 기록 | `modules/config.py`, 각 생성 모듈의 `try/except`, `main.py`의 `errors` 리스트 |
| 10 | API 키 관리 | API 키를 코드에 직접 작성하지 않고 `.env` 파일(환경변수)에서 읽어옴 | `modules/config.py` |

> `.env` 파일은 로컬에서 직접 생성하는 실제 키 파일이며, Git에는 커밋되지 않습니다(`.gitignore`에 등록). 별도의 `.env.example` 템플릿 파일은 이 프로젝트에 포함되어 있지 않습니다.

## 📌 시스템 설계

### 1. 전체 파이프라인

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

💡 **왜 이 순서인가**

| 설계 결정 | 이유 |
|---|---|
| 브리프 검증을 가장 먼저 | 잘못된 입력으로 인한 불필요한 API 비용 낭비 방지 |
| 텍스트 4단계를 이미지보다 먼저 | 이미지 생성이 텍스트보다 느리고 비용이 높음. 또한 로고 프롬프트가 네이밍/컬러 결과를 참조하므로 순서상 텍스트가 먼저 끝나야 함 |
| 각 단계를 개별 `try-except`로 분리 | 하나의 API 호출 실패가 전체 파이프라인을 중단시키지 않도록 함  |
| JSON 저장을 맨 마지막에 | 중간에 일부 단계가 실패해도, 그때까지 성공한 결과만이라도 최종 저장 가능 |

### 2. 기술 스택과 선정 이유

| 구분 | 선택 | 이유 |
|---|---|---|
| 텍스트 생성 API | OpenAI `gpt-4o-mini` | 저비용으로 빠르게 JSON 구조화 응답(`response_format={"type": "json_object"}`)을 안정적으로 받을 수 있음 |
| 이미지 생성 API | OpenAI `gpt-image-1` | 기존 `dall-e-3`는 2026년 5월 12일 OpenAI에서 완전히 폐지되어 더 이상 호출이 불가능함. 후속 모델인 `gpt-image-1`을 사용  |
| 컬러 시각화 | matplotlib | 요구사항에 명시된 라이브러리. `Rectangle` 패치로 색상 블록을 직접 그려 세밀한 커스터마이징(라벨, 텍스트 색 자동 대비 등) 가능 |
| 환경변수 관리 | python-dotenv | `.env` 파일을 코드 수정 없이 읽어와 API 키를 코드에서 완전히 분리 |
| HTTP 요청 | requests | 이미지 생성 API가 URL 방식으로 응답할 경우 다운로드용 (b64_json 미제공 시 대비) |

💡 **하나의 API 키로 충분한 이유**:  

> OpenAI는 텍스트(GPT)와 이미지(gpt-image-1) 모두 동일 `OPENAI_API_KEY` 하나로 호출 가능  



### 3. 핵심 라이브러리

#### 🛠️ 외부 라이브러리 (`requirements.txt`)

| 라이브러리 | 버전 | 용도 | 사용 위치 |
|---|---|---|---|
| `openai` | `>=1.30.0` | OpenAI 공식 SDK. Chat Completions API로 `gpt-4o-mini` 텍스트 생성(네이밍/슬로건/스토리/컬러), Images API로 `gpt-image-1` 로고 이미지 생성을 모두 이 하나의 SDK로 호출 | `modules/text_generator.py`, `modules/image_generator.py` |
| `python-dotenv` | `>=1.0.0` | `.env` 파일을 읽어 `OPENAI_API_KEY`를 환경변수로 자동 등록. API 키를 코드에서 완전히 분리하기 위한 핵심 라이브러리 (요구사항 10번) | `modules/config.py` |
| `matplotlib` | `>=3.7.0` | 컬러 팔레트를 `Rectangle` 도형으로 그려 PNG로 저장. `font_manager`로 OS별 한글 폰트를 자동 탐색/등록하는 로직도 이 라이브러리 기반 | `modules/palette_visualizer.py` |
| `Pillow` | `>=10.0.0` | `requirements.txt`에 명시되어 있으나, 현재 코드베이스에서는 `PIL`/`Image`를 import하는 곳이 없어 실제로는 사용되지 않는 의존성임 (matplotlib이 내부적으로 의존할 수 있어 남아있을 뿐, 직접 호출 코드는 없음) | — (미사용) |
| `requests` | `>=2.31.0` | 이미지 생성 API가 `url` 형식으로 응답할 경우 이미지를 다운로드하기 위한 HTTP 클라이언트 (기본 응답은 `b64_json`이라 실제로는 예비 경로) | `modules/image_generator.py` |


#### 🛠️ 파이썬 표준 라이브러리

이 프로젝트는 별도 설치 없이 파이썬에 기본 내장된 모듈도 적극 활용함.

| 모듈 | 용도 | 사용 위치 |
|---|---|---|
| `os` | 파일/폴더 존재 확인, 경로 조합(`os.path.join`), 출력 폴더 생성(`os.makedirs`) | 거의 모든 모듈 |
| `sys` | API 키 누락, 브리프 오류 등 치명적 상황에서 `sys.exit()`로 프로그램 종료 | `main.py`, `modules/config.py` |
| `json` | 브리프 파일 파싱, LLM의 JSON 응답 파싱, 최종 결과(`brand_result.json`) 저장 | `modules/brief_loader.py`, `modules/text_generator.py`, `modules/result_saver.py` |
| `base64` | 이미지 생성 API가 반환하는 `b64_json` 문자열을 실제 PNG 바이트로 디코딩 | `modules/image_generator.py` |
| `datetime` | 결과 생성 시각(`generated_at`)을 ISO 8601 형식으로 기록 | `modules/result_saver.py` |





### 4. 입력 스펙 — 브랜드 브리프

| 필드 | 필수 | 타입 | 설명 | 예시 |
|---|---|---|---|---|
| `industry` | ✅ | string | 업종 | `"스페셜티 커피 전문점"` |
| `target` | ✅ | string | 타겟 고객 | `"20~30대 직장인, 커피 애호가"` |
| `keywords` | ✅ | array 또는 콤마 구분 string | 핵심 키워드 | `["신선함", "정직한 원두"]` |
| `tone` | ⬜ | string | 톤앤매너 | `"친근하지만 전문적인"` |
| `competitors` | ⬜ | string/array | 경쟁사 (프롬프트 컨텍스트로만 참고됨) | `"블루보틀, 프릳츠"` |
| `notes` | ⬜ | string | 추가 요청사항 | `"과하지 않은 편안한 느낌"` |  


🔹입력 파일 예시(brief.json)

```json
{
  "industry": "스페셜티 커피 전문점",
  "target": "20~30대 직장인, 원두 품질을 중시하는 커피 애호가",
  "keywords": ["신선함", "정직한 원두", "따뜻한 공간", "로컬"],
  "tone": "친근하지만 전문적인, 감성적인",
  "competitors": "블루보틀, 프릳츠커피컴퍼니",
  "notes": "동네 골목상권에 위치한 소규모 로스터리 카페입니다. 과하지 않은 편안한 느낌을 원해요."
}
```

🔹 `brief_loader.py`는 `keywords`가 문자열로 들어와도 콤마 기준으로 자동 분리하며, 선택 필드가
없으면 빈 문자열로 기본값을 채워 이후 로직에서 `KeyError` 없이 안전하게 동작하도록 함.


### 5. 출력 스펙 — 결과 파일

```
output/
├── brand_result.json     # 모든 텍스트 결과 + 생성 파일 목록
├── color_palette.png     # 컬러 팔레트 시각화
├── logo_01.png            # 로고 시안 1
├── logo_02.png            # 로고 시안 2
└── logo_03.png            # 로고 시안 3
```

🔹 `brand_result.json` 구조 (`result_saver.py` 기준):

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
  },
  "errors": [
    {
      "step": "슬로건 생성",
      "error_type": "RateLimitError",
      "message": "API 요청 한도(rate limit)를 초과했습니다. 잠시 후 다시 시도해주세요.",
      "occurred_at": "2026-08-22T12:31:50"
    }
  ]
}
```

🔹 `errors`는 실패한 단계가 없으면 빈 배열(`[]`)로 저장됨. 각 항목은 `step`(어떤 단계인지),
`error_type`(예외 클래스명), `message`(사용자에게 출력된 메시지와 동일한 설명),
`occurred_at`(발생 시각)으로 구성되어, 결과 파일만 열어봐도 어떤 단계가 왜 실패했는지 사후에
파악할 수 있음.  

## 📌 프로젝트 파일 구조

```
brand-ai-generator/
├── main.py                       # CLI 진입점 (전체 실행 흐름 제어)
├── requirements.txt               # 설치가 필요한 패키지 목록
├── .env                           # 실제 API 키 (직접 생성, Git 추적 제외)
├── .gitignore                     # Git이 추적하지 않을 파일/폴더 목록
├── brief.json                     # 브랜드 브리프
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

💡 **왜 이렇게 나눴나**   

> 단일 책임 원칙에 따라 파일 하나 = 역할 하나로 분리했음.
> 새로운 생성 기능(예: 홍보 문구 생성)을 추가하려면 `text_generator.py`에 함수 하나만 추가하고 `main.py`에서 호출 한 줄만 추가하면 되는 구조.

## 📌 모듈별 상세 설계

### `main.py` — CLI 오케스트레이션

- `get_user_input()`: 브리프 경로(필수, 빈 값이면 재입력 루프)와 출력 폴더(선택, 기본 `./output`)를 입력.
- `print_naming_result()` 등 4개의 `print_*_result()` 함수: 각 단계의 생성 결과를 [실행 결과 예시]와 동일한 포맷으로 출력. 네이밍 의미 설명은 **15자를 넘으면 자동으로 잘라 `...`을 붙이는 안전장치**가 있음 (프롬프트로 15자를 요청하지만, LLM이 이를 넘길 가능성에 대비한 이중 안전망).
- `main()`: 5단계를 순서대로 호출하고, 각 단계 사이에 `[N/5] ... 생성 중...` 헤더를 출력.

### `modules/config.py` — API 키 관리

- `python-dotenv`로 `.env` 파일을 자동 로드 (설치가 안 되어 있어도 예외 처리로 프로그램이 죽지 않음).
- `get_openai_api_key()`: 키가 없으면 `.env` 작성법과 환경변수 직접 설정법을 안내하고 `sys.exit(1)`로 즉시 종료. 키가 있지만 `sk-`로 시작하지 않으면 경고만 출력하고 계속 진행. (실제 유효성은 API 호출 시점에 판별).

### `modules/brief_loader.py` — 브리프 검증

- 파일 존재 여부, JSON 문법, 필수 필드(`industry`/`target`/`keywords`) 3가지를 순서대로 검사.
- `keywords`가 배열이 아니라 문자열로 들어와도(`"신선함, 정직함"`) 자동으로 콤마 분리해 배열로 변환 — 사용자가 JSON 문법에 서툴러도 유연하게 동작하도록 한 설계.

### `modules/text_generator.py` — 텍스트 브랜드 요소 생성

4개의 생성 함수(`generate_naming`, `generate_slogans`, `generate_story`, `generate_color_palette`)가
모두 공통 헬퍼 `_call_json_with_clarification()`을 통해 `response_format={"type": "json_object"}` 옵션으로
OpenAI Chat Completions API를 호출. LLM이 설명 문장을 덧붙이지 않고 순수 JSON만 반환하도록 강제함.

💡 **프롬프트 설계 원칙** (실제 코드에 적용된 5가지):  

| 원칙 | 적용 예시 |
|---|---|
| 🔹역할 부여 | "당신은 전문 브랜드 네이밍 컨설턴트입니다" |
| 🔹명확한 지시 | "브랜드명 후보를 3~5개 제안해주세요" |
| 🔹컨텍스트 제공 | `_build_brief_context()`가 industry/target/keywords/tone/competitors/notes를 프롬프트에 포함 |
| 🔹출력 형식 지정 | `{"names": [{"name": "...", "meaning": "..."}]}` 형태를 프롬프트에 명시 |
| 🔹제약 조건 | 네이밍 의미는 "15자 이내", 스토리는 "300자 내외", 컬러는 "반드시 #RRGGBB 형식" |

> `generate_naming()`은 특히 의미 설명 길이 제약이 까다로워, "완전한 문장이 아니라 명사구로
> 끝낼 것", "말줄임표/마침표 금지"까지 명시해 모델이 15자 제약을 지키도록 강하게 유도함.

> 모든 함수는 실패 시 예외를 상위로 던지지 않고 `_handle_api_error()`로 로그만 남긴 뒤 `None`을
> 반환해, `main.py`가 다음 단계로 계속 진행할 수 있게 함.  

### `modules/image_generator.py` — 로고 시안 생성

- `_build_logo_prompt()`: 네이밍 1순위 결과와 메인 컬러 HEX 코드를 영문 프롬프트에 삽입해
  텍스트 생성 결과가 로고 디자인에 반영되도록 함.
- `generate_logos()`: `LOGO_COUNT`(기본 3)만큼 반복하며, 파일명은 `logo_01.png`처럼 2자리
  zero-padding으로 저장. 각 로고는 아래 2단계 안전장치를 거쳐 **항상 파일이** 
  **저장되도록** 설계되어 있음.
  1. **재시도(`_generate_one_logo()`)**: `RateLimitError`/`APIConnectionError`/`APIError`처럼
     시간이 지나면 성공할 가능성이 있는 "일시적" 오류는 지수 백오프(2초 → 4초)로
     `RETRY_LIMIT`(기본 2)회까지 재시도. 인증 오류(`AuthenticationError`)는 재시도해도
     결과가 같으므로 즉시 실패 처리.
  2. **플레이스홀더(`_save_placeholder_logo()`)**: 재시도까지 모두 실패하면 matplotlib으로
     브랜드명 첫 글자 + 메인 컬러를 담은 대체 이미지를 직접 그려 저장. 이 덕분에
     이미지 API가 완전히 다운되는 최악의 상황에서도 `logo_images`가 빈 배열로 남지 않고
     요구사항(로고 2~3개 PNG)을 항상 충족함. 플레이스홀더 사용 여부는
     `errors`에 `"error_type": "PlaceholderUsed"`로 별도 기록되어, 어떤 로고가 AI 생성인지
     대체 이미지인지 결과 파일만으로 구분할 수 있음.
- 이미지 API 응답은 SDK/모델 버전에 따라 `b64_json` 또는 `url` 둘 중 하나로 올 수 있어, 두
  경우를 모두 처리하도록 방어적으로 작성되어 있음 (`response_format` 파라미터는 일부
  모델/SDK 조합에서 지원되지 않으므로 아예 넘기지 않음).

###  `modules/palette_visualizer.py` — 컬러 팔레트 시각화

- `_set_korean_font()`: OS별 한글 폰트(Windows `Malgun Gothic`, macOS `AppleGothic`,
  Linux `NanumGothic`/`Noto Sans CJK KR`)를 자동 탐색해 matplotlib에 등록. 이 처리가
  없으면 한글 라벨이 네모(□)로 깨져 보임.
- `save_palette_image()`: 메인 컬러 + 서브 컬러를 `Rectangle`로 그리고, `is_light_color()`로
  각 색상의 밝기(YIQ 공식 기반)를 계산해 텍스트 색을 흑/백으로 자동 전환함 — 밝은 색
  배경에 흰 글씨, 어두운 색 배경에 검은 글씨가 겹쳐 안 보이는 문제를 방지함. (`is_light_color()`는
  `image_generator.py`의 플레이스홀더 로고에서도 재사용되는 공개 함수임)

### `modules/result_saver.py` — 최종 결과 저장

- 네이밍/슬로건/스토리/컬러 중 실패한 항목이 있어도 `None`을 빈 값(`[]`, `""`, `{}`)으로
  치환해 JSON 저장이 항상 성공하도록 함. 이것이 "부분 실패 허용 파이프라인"의 마지막
  안전장치.

## 📌 핵심 설계 원칙

### ✅ 부분 실패를 허용하는 파이프라인

```python
# 나쁜 예 — 하나 실패하면 전부 날아감
try:
    naming = generate_naming()
    slogans = generate_slogans()
    story = generate_story()
except Exception as e:
    print(f"실패: {e}")

# 이 프로젝트의 방식 — 각 단계를 독립적으로 처리하고 실패는 errors 리스트에 기록
errors = []
naming = generate_naming(client, brief, errors)     # 실패해도 None 반환 + errors에 기록
slogans = generate_slogans(client, brief, errors)   # naming 실패와 무관하게 계속 실행
story = generate_story(client, brief, errors)
colors = generate_color_palette(client, brief, errors)
# → 4개 중 몇 개가 실패하든, 성공한 결과 + 실패 기록(errors)이 함께 brand_result.json에 저장됨
```

🔹 **실패 기록까지 남기는 이유** — 단순히 실패해도 넘어가는 것만으로는 부족함. 나중에
`brand_result.json` 파일만 열어봤을 때 "어떤 단계가 왜 실패했는지"를 알 수 없다면 디버깅이나
재실행 판단이 불가능. 그래서 이 프로젝트는 각 생성 함수에 `errors` 리스트를 공유
전달하여, 실패 시 `_handle_api_error()`(텍스트 생성) / `_record_error()`(이미지 생성)가
`{"step": ..., "error_type": ..., "message": ..., "occurred_at": ...}` 형태로 기록을
추가. 이 리스트는 `main.py`에서 생성되어 모든 단계에 걸쳐 누적된 뒤,
`result_saver.py`를 통해 최종 JSON의 `"errors"` 필드로 저장.

### ✅ 이중 안전망(dual safety net) 패턴

이 프로젝트는 "AI 응답이 제약을 어길 가능성"에 대해 프롬프트 지시 + 코드 검증의 2단계 방어를
사용. 대표적으로 네이밍 의미 설명의 15자 제한이 있음.

1. **1차 방어 (프롬프트)**: `text_generator.py`의 `generate_naming()` 프롬프트에서 "15자를
   넘지 않을 것"을 여러 번 강조
2. **2차 방어 (코드)**: `main.py`의 `print_naming_result()`가 15자를 초과하면 강제로 잘라
   `...`을 붙임

이렇게 하면 LLM이 지시를 완벽히 지키지 못하더라도 최종 출력은 항상 요구사항을 만족함.

### ✅ 모델/SDK 버전 변화에 대한 방어적 설계

`image_generator.py`는 `response_format` 파라미터를 아예 사용하지 않고, 응답에 `b64_json`이
있으면 디코딩하고 없으면 `url`을 다운로드하는 방식으로 작성되어 있음. 이는 실제로 개발
중 `dall-e-3` 모델 폐지와 파라미터 미지원 오류를 겪은 뒤 반영한 설계.

## 📌 에러 처리 가이드

이 프로그램은 **한 단계가 실패해도 전체가 멈추지 않고, 실패한 단계만 건너뛰고 계속 진행**하는
것을 기본 원칙으로 함.

| 오류 상황 | 발생 원인 | 프로그램의 대응 | 사용자가 해야 할 일 |
|---|---|---|---|
| **API 키 누락** (`OPENAI_API_KEY` 없음) | `.env` 파일을 만들지 않았거나 환경변수 미설정 | 프로그램 시작 직후 감지하여 안내 메시지 출력 후 **즉시 종료** (`sys.exit(1)`) | `.env` 파일에 `OPENAI_API_KEY=sk-...` 추가 |
| **API 키 인증 실패** (`AuthenticationError`) | 키 값이 잘못되었거나 만료/폐기됨 | 해당 단계에서 에러 메시지 출력 후 **해당 단계만 건너뛰고 다음 단계 진행** (로고 시안의 경우, `generate_logos()`는 인증 오류가 나도 루프를 중단하지 않고 남은 로고마다 동일하게 실패 처리한 뒤 각각 플레이스홀더 이미지로 대체 저장함) | OpenAI 대시보드에서 키 상태 확인, 새 키 발급 후 `.env` 갱신 |
| **API 요청 한도 초과** (`RateLimitError`) | 짧은 시간에 너무 많은 요청, 또는 사용량/결제 한도 초과 | 에러 메시지 출력 후 해당 단계를 건너뛰고 계속 진행 | 잠시 후 재실행, 또는 OpenAI 결제 정보/한도 확인 |
| **네트워크 연결 오류** (`APIConnectionError`) | 인터넷 연결 불안정, 방화벽/프록시 차단 | 에러 메시지 출력 후 해당 단계를 건너뛰고 계속 진행 | 네트워크 상태 확인 후 재실행 |
| **OpenAI 서버 오류** (`APIError`, 4xx/5xx) | 모델 폐지, 파라미터 미지원, 서버 일시 장애 등 | 에러 메시지 출력 후 해당 단계를 건너뛰고 계속 진행 | 오류 메시지의 `code`/`message` 확인, 잠시 후 재시도 |
| **JSON 파싱 실패** (`JSONDecodeError`) | LLM 응답이 JSON 형식이 아니거나 형식이 깨짐 | 에러 메시지 출력 후 해당 단계 결과를 빈 값으로 처리, 다음 단계 진행 | 재실행 시 대부분 정상 생성됨 (모델 응답의 변동성) |
| **브리프 파일 없음/경로 오류** | 사용자가 잘못된 경로 입력 | `[브리프 오류]` 메시지 출력 후 프로그램 종료 | 올바른 파일 경로 재입력 |
| **브리프 JSON 형식 오류** | JSON 문법 오류(콤마 누락 등) | 오류 위치와 함께 메시지 출력 후 프로그램 종료 | JSON 문법 검사 후 재실행 (예: jsonlint.com) |
| **브리프 필수 필드 누락** | `industry`/`target`/`keywords` 중 하나라도 없음 | 누락된 필드명을 출력하고 프로그램 종료 | 브리프 파일에 필수 필드 추가 후 재실행 |
| **로고 이미지 저장 실패** (디스크/권한 문제) | 출력 폴더 쓰기 권한 없음, 디스크 용량 부족 등 | 에러 메시지 출력 후 해당 로고만 건너뛰고 다음 로고 계속 생성 | 출력 폴더 권한/용량 확인 |

> 설계 원칙: 텍스트 생성과 이미지 생성은 서로 독립적으로 동작하므로,
> 예를 들어 로고 생성에 전부 실패하더라도 이미 만들어진 네이밍/슬로건/스토리/컬러 결과는
> 정상적으로 `brand_result.json`에 저장됨.

✅ 오류 화면 (스크린 샷)

|API KEY 설정 오류| 이미지 생성 모델(dall-e)오류|입력파일 오류|
|---|---|---|
|<img width="812" height="391" alt="image" src="https://github.com/user-attachments/assets/9c47fd7a-7b03-4f45-a7c8-5759b0861c5a" />|<img width="1612" height="789" alt="image" src="https://github.com/user-attachments/assets/9cd7bc68-dd2a-4902-b590-13ed8113c2c2" />|<img width="613" height="179" alt="image" src="https://github.com/user-attachments/assets/7c523e07-51d7-4e34-8f08-a37d9bcd20f9" />|




## 📌 개발 환경 설정 

Python을 처음 다뤄보는 분도 순서대로 따라 할 수 있도록 단계별로 정리했습니다.

### STEP 1. Python 설치 확인

```bash
python3 --version
# Windows에서는
python --version
```

`Python 3.9` 이상이면 정상입니다. 
설치되어 있지 않다면 [python.org](https://www.python.org/downloads/)에서 설치 파일을 내려받아 설치.   
(Windows는 설치 시 **"Add Python to PATH"** 체크 필수)

### STEP 2. 프로젝트 폴더로 이동

```bash
cd brand-ai-generator
```

### STEP 3. 가상환경(venv) 생성 및 활성화

✅ 가상환경(venv)이란?

- **정의**: 파이썬 설치 위에 독립적인 환경을 만드는 기능.  
  각 환경은 자체적인 **파이썬 인터프리터와 site-packages 디렉터리**를 가짐.
- **역할**: 특정 프로젝트에서만 필요한 라이브러리 버전을 설치하고, 다른 프로젝트와 격리시킴.

✅ venv를 쓰는 이유  

| 문제 상황 | venv 사용 시 해결 방법 |
|-----------|-----------------------|
| 프로젝트 A는 `requests==2.6.0` 필요, 프로젝트 B는 `requests==3.0.0` 필요 | 각 프로젝트별 가상환경을 만들어 충돌 방지 |
| 운영체제 전체에 패키지를 설치하면 다른 프로그램에 영향 | venv는 **프로젝트 전용 환경**이므로 안전 |
| 협업 시 동일한 환경을 맞추기 어려움 | `requirements.txt`로 환경을 공유하면 누구나 같은 환경 재현 가능 |
| 테스트용으로 특정 버전의 라이브러리만 필요 | 가상환경을 쉽게 만들고 삭제할 수 있어 실험에 적합 |

✅ venv의 장점
- **격리성**: 다른 프로젝트와 독립적으로 패키지를 관리
- **재현성**: `requirements.txt`로 동일한 환경을 쉽게 복원
- **안전성**: 시스템 전체 파이썬 환경을 건드리지 않음
- **유연성**: 필요할 때마다 새로운 환경을 만들고 삭제 가능

🚨 주의할 점
- 프로젝트 코드와 가상환경을 섞지 말 것
- venv 디렉터리는 보통 `.gitignore`에 추가
- 환경 이름은 `.venv` 또는 `venv`를 많이 사용 (숨김 처리 및 툴 호환성 때문)



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

### STEP 5. API 키 설정 및 `.env` 설정

1. [OpenAI API 키 발급 페이지](https://platform.openai.com/api-keys)에서 API 키를 발급  
2. 프로젝트 루트에 `.env` 파일 생성   
3. `.env` 파일을 열어 발급받은 키를 입력  

```
OPENAI_API_KEY=sk-발급받은실제키값
```

> ⚠️ `.env` 파일은 `.gitignore`에 등록되어 있어 Git에 커밋되지 않음 
> 절대로 API 키를 코드에 직접 작성하거나 GitHub에 올리지 마세요!


**✅ 환경변수 관리 이유**

       API 키를 소스코드에 직접 작성하면 GitHub 업로드, 화면 공유, 코드 제출 과정에서 쉽게 유출될 수 있습니다.
       따라서 환경변수 또는 .env 파일로 분리하여 관리하는 것이 안전합니다.  
    
🔹 보안: API 키를 코드에 직접 작성하면 깃허브 등 공개 저장소에 유출될 위험이 있음  
🔹 유연성: 개발/운영 환경마다 다른 키를 쉽게 적용 가능  
🔹 재사용성: 여러 프로젝트에서 동일한 키를 공유할 때 편리  

🔹 원칙: .env 파일 → dotenv 라이브러리 → os.getenv()로 불러오기   

*API 키는 매우 중요한 민감정보이므로 아래 사항을 반드시 지켜야 합니다.*

🔹주의사항
   - API 키를 코드에 직접 작성하지 않는다.
   - .env 파일은 GitHub에 업로드하지 않는다.
   - .gitignore에 .env를 반드시 포함한다.
   - 화면 캡처, 발표 자료, 제출 문서에 키가 보이지 않도록 주의한다.
   - 키가 노출되었다면 즉시 폐기하고 새 키를 발급받는다. 


### STEP 6. 실행

```bash
python3 main.py
```

### STEP 7. 가상환경 종료 (작업 종료 시)

```bash
deactivate
```

## 📌 Git 사용법 및 실전 트러블슈팅

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

> 💡 마지막 줄의 `-u` 옵션이 핵심. 
> `-u`(`--set-upstream`)를 붙여 push하면 로컬 `main`과 원격 `origin/main`이 자동으로 "짝(tracking)"으로 연결되어, 이후에는
> `git pull`, `git push`만 입력해도 자동으로 동기화됨.

### ⚠️ 실전에서 겪은 문제와 해결 (원인 → 해결 순)

**1) `git add .` 시 "LF will be replaced by CRLF..." 경고**

- **원인**: Windows(CRLF)와 Git 저장소 기준(LF)의 줄바꿈 문자가 달라서 Git이 자동 변환
  중이라는 **안내일 뿐, 오류가 아님**.
- **해결**: 그냥 무시하고 진행해도 무방. 경고 자체를 없애려면 `.gitattributes`에
  `* text=auto eol=lf`를 추가하면 됨 (현재 프로젝트에는 `.gitattributes` 파일이 포함되어
  있지 않으므로, 경고를 없애고 싶다면 프로젝트 루트에 직접 생성해야 함).

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

## 📌 실행 방법 및 결과 예시

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

    브리프 파일 경로를 입력하세요: brief.json
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

> API 호출이 실패하는 단계가 있어도 해당 단계의 실패 메시지만 출력되고 나머지 단계는 계속 진행됩니다.  



✅ 정상 실행 화면 (스크린 샷)

| 입력 파일(json) |정상 실행 스크린샷| 결과물(파일저장) 스크린샷|
|---|---|---|
|<img width="300" height="198" alt="image" src="https://github.com/user-attachments/assets/cfef4d20-86cc-4196-8373-ea8fbdf041c2" />|<img width="523" height="638" alt="image" src="https://github.com/user-attachments/assets/4929f484-0559-45b4-87f9-a3b62624c77d" />|<img width="421" height="209" alt="image" src="https://github.com/user-attachments/assets/0a23697b-9f10-40c8-9ace-0c42d85b3101" />|

> 실행이 끝나면 `output/` 폴더(또는 직접 지정한 폴더)에 아래 파일들이 생성됨

- `brand_result.json` — 네이밍, 슬로건, 스토리, 컬러 정보, 생성된 파일 목록
- `color_palette.png` — 컬러 팔레트 시각화 이미지
- `logo_01.png`, `logo_02.png`, `logo_03.png` — AI가 생성한 로고 시안


## 📌 알려진 이슈 및 대응 기록

개발 및 실제 사용 과정에서 발견되어 코드에 반영된 이슈들임. 같은 문제를 겪을 다른
사용자를 위해 원인과 해결을 기록으로 남김

| 이슈 | 증상 | 원인 | 조치 |
|---|---|---|---|
| `dall-e-3` 모델 폐지 | `Error code: 400 - The model 'dall-e-3' does not exist` | OpenAI가 2026년 5월 12일부로 `dall-e-3`를 완전히 서비스 종료(retire)함 | `IMAGE_MODEL`을 `gpt-image-1`로 교체 (`modules/image_generator.py`) |
| `response_format` 파라미터 미지원 | `Error code: 400 - Unknown parameter: 'response_format'` | 설치된 SDK/모델 조합이 이미지 생성 API의 `response_format` 파라미터를 받지 않음 | 파라미터를 아예 넘기지 않고, 응답의 `b64_json`/`url` 여부를 코드에서 분기 처리 |
| 네이밍 설명이 너무 길어짐 | 한 줄 출력이 여러 줄로 늘어남 | LLM이 프롬프트의 길이 제약을 완벽히 지키지 않는 경우가 있음 | 프롬프트에 15자 제한을 여러 차례 명시 + `main.py`에 15자 초과 시 자동 절단하는 코드 안전장치 추가  |
| 한글이 네모(□)로 깨짐 | matplotlib 팔레트 이미지의 한글 라벨이 깨짐 | matplotlib 기본 폰트가 한글을 지원하지 않음 | `palette_visualizer.py`에 OS별 한글 폰트 자동 탐색/등록 로직 추가 |


## 📌 이 프로젝트로 배우는 것


- ✅ **LLM API 사용법**: OpenAI 같은 AI로 텍스트 만들기

      OpenAI(ChatGPT) 같은 AI 서비스에 인터넷으로 질문을 보내고 답변을 받는 방법을 배움

   📝 이 프로젝트에서 배우는 부분

            from openai import OpenAI

            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "브랜드 이름 3개 추천해줘"}]
            )
            print(response.choices[0].message.content)

- ✅ **이미지 생성 AI**: gpt-image-1로 이미지 만들고 저장하기

    텍스트 설명을 입력하면 그림을 그려주는 AI를 사용하는 방법을 배움.
    텍스트뿐만 아니라 이미지도 자동으로 생성할 수 있게 되면, 만들 수 있는 서비스의 폭이 훨씬 넓어짐. (썸네일 자동 생성, 로고 제작, 일러스트 등)

    > ⚠️ 기존 `dall-e-3` 모델은 2026년 5월 12일 OpenAI에서 완전히 폐지(retire)되어 더 이상
    > 호출할 수 없습니다. 후속 모델인 `gpt-image-1`을 사용합니다.

      📝 이 프로젝트에서 배우는 부분
      modules/image_generator.py에서 "친환경 화장품 브랜드의 미니멀한 로고" 같은 설명으로 로고 이미지 만들기
      생성된 이미지를 디코딩/다운로드해서 PNG 파일로 저장하기

            response = client.images.generate(
                model="gpt-image-1",
                prompt="자연주의 화장품 브랜드의 미니멀한 로고, 초록색 계열",
                size="1024x1024",
                n=1,
            )
            data = response.data[0]
            # gpt-image-1은 보통 b64_json으로 응답하지만, SDK/모델 버전에 따라
            # url로 올 수도 있어 두 경우를 모두 처리하도록 작성함
            if data.b64_json:
                image_bytes = base64.b64decode(data.b64_json)
            else:
                image_bytes = requests.get(data.url).content

- ✅ **JSON 형태로 답변 받기**: AI가 정해진 형식으로 대답하게 만들기

      📝 이 프로젝트에서 배우는 부분
      OpenAI의 response_format={"type": "json_object"} 옵션 사용하기
      직접 작성한 검증 함수로 응답 스키마가 올바른지 확인하기
      스키마가 틀리면 "여기가 잘못됐다"고 모델에게 알려주고 다시 응답받는 재질문(clarification) 루프

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                response_format={"type": "json_object"},  # ← JSON 형식 강제!
                messages=[...]
            )
            data = json.loads(response.choices[0].message.content)
            names = data["names"]  # 바로 사용 가능!

            # 스키마 검증 예시 (text_generator.py의 실제 방식)
            def _validate_naming(result):
                names = result.get("names")
                if not isinstance(names, list) or len(names) == 0:
                    return False, "'names' 필드가 배열이 아니거나 비어 있습니다."
                for item in names:
                    if "name" not in item or "meaning" not in item:
                        return False, "각 항목에 'name'과 'meaning'이 필요합니다."
                return True, None
            # 검증 실패 시, 문제를 구체적으로 지적하는 메시지를 이어붙여 최대 2회 재질문

- ✅ **여러 작업 순서 관리**: 여러 API 호출을 차례대로 처리하기

      📝 이 프로젝트에서 배우는 부분
      main.py에서 각 생성 함수를 순서대로 호출하기
      이전 단계 결과를 다음 단계 입력으로 넘기기 (예: 이름 + 컬러 → 로고 프롬프트에 활용)
      각 단계의 실패 정보를 errors 리스트에 모아 최종 결과에 함께 저장하기

            errors = []
            naming = generate_naming(client, brief, errors)
            slogans = generate_slogans(client, brief, errors)
            story = generate_story(client, brief, errors)
            colors = generate_color_palette(client, brief, errors)

            if colors:
                save_palette_image(colors, output_dir)

            # 로고는 네이밍 결과 + 메인 컬러를 프롬프트에 반영
            logo_paths = generate_logos(client, brief, naming, colors, output_dir, errors)

            save_json_result(brief, naming, slogans, story, colors, logo_paths, output_dir, errors)

- ✅ **오류 대응**: 일부 실패해도 계속 진행되는 튼튼한 프로그램 만들기

      API 호출이 실패했을 때 프로그램이 죽지 않고, 다시 시도하거나 대체 방안을 실행하는 방법을 배움.
      이 프로젝트는 실패 유형에 따라 두 가지 다른 대응 방식을 사용함.

      📝 이 프로젝트에서 배우는 부분
      ① try-except로 각 생성 단계 감싸기 (하나 실패해도 나머지는 계속 진행)
      ② 로고 이미지: 일시적 오류(요청 한도/네트워크/서버)는 지수 백오프로 최대 2회 재시도,
         그래도 실패하면 matplotlib으로 그린 플레이스홀더 이미지로 대체 저장
      ③ 텍스트 생성: 스키마 위반 시 재질문 최대 2회, 그래도 실패하면 해당 단계만 건너뛰기
      ④ 부분 실패 허용: 로고 생성이 전부 실패해도 이름/슬로건/스토리/컬러는 정상 저장

            import time

            for attempt in range(RETRY_LIMIT + 1):  # RETRY_LIMIT = 2 → 총 3회 시도
                try:
                    return client.images.generate(...)
                except (RateLimitError, APIConnectionError, APIError):
                    if attempt < RETRY_LIMIT:
                        time.sleep(2 ** (attempt + 1))  # 2초, 4초 대기 후 재시도
                    else:
                        return save_placeholder_logo(...)  # 최종 대체 저장

- ✅ **API 키 안전하게 다루기**: 환경변수로 비밀 정보 관리하기

      📝 이 프로젝트에서 배우는 부분
      .env 파일에 API 키 저장하기
      python-dotenv로 불러오기
      .gitignore에 .env 추가해서 GitHub 업로드 방지
      키가 없거나 형식이 이상하면(예: 'sk-'로 시작 안 함) 명확한 안내 메시지 출력하기

            # .env 파일
            OPENAI_API_KEY=sk-proj-xxxxx

            # 파이썬 코드 (modules/config.py)
            from dotenv import load_dotenv
            import os, sys

            load_dotenv()
            api_key = os.getenv("OPENAI_API_KEY", "").strip()
            if not api_key:
                print("OPENAI_API_KEY가 설정되어 있지 않습니다. .env 파일을 확인해주세요.")
                sys.exit(1)

- ✅ **색상 시각화**: matplotlib으로 색상 팔레트 그리기

      AI가 알려준 색상 코드(예: #5D7B6F)를 실제 눈으로 볼 수 있는 이미지(PNG)로 만드는 방법을 배움.
      "main": "#5D7B6F"라는 텍스트만 봐서는 어떤 색인지 모름. 팔레트 이미지로 만들어야 클라이언트가 "아, 이런 느낌이구나!" 하고 이해할 수 있음.

      📝 이 프로젝트에서 배우는 부분
      matplotlib으로 색상 사각형 그리기
      배경 밝기를 계산해서 텍스트 색을 흑/백으로 자동 전환하기 (밝은 배경엔 검은 글씨)
      OS별 한글 폰트를 자동 탐색/등록해서 한글 라벨이 깨지지 않게 하기
      PNG 파일로 저장하기 (color_palette.png)

            import matplotlib.pyplot as plt

            colors = ["#5D7B6F", "#E8DFCA", "#A8B5A0"]
            fig, ax = plt.subplots(figsize=(len(colors) * 2, 3))
            for i, color in enumerate(colors):
                ax.add_patch(plt.Rectangle((i, 0), 1, 1, color=color))
                ax.text(i + 0.5, 0.5, color, ha="center", va="center")
            ax.set_xlim(0, len(colors))
            plt.savefig("output/color_palette.png", dpi=150, bbox_inches="tight")

- ✅ **CLI 만들기**: 명령어로 실행하는 대화형 프로그램 설계

      이 프로젝트는 argparse 같은 명령줄 옵션(--brief, --output) 방식이 아니라,
      input()을 사용한 완전 대화형(interactive) CLI로 만들어져 있음.
      실행하면 프로그램이 먼저 질문을 하고, 사용자가 값을 입력하면 그 값으로 실행되는 방식.

            $ python main.py

      📝 이 프로젝트에서 배우는 부분
      input()으로 사용자 입력 받기 (필수 값은 빈 입력이면 다시 물어보는 재입력 루프)
      선택 입력은 엔터만 치면 기본값(./output)을 사용하도록 처리하기

            # main.py의 실제 방식
            def get_user_input():
                brief_path = input("    브리프 파일 경로를 입력하세요: ").strip()
                while not brief_path:
                    print("    브리프 파일 경로는 필수 입력값입니다.")
                    brief_path = input("    브리프 파일 경로를 입력하세요: ").strip()

                output_dir = input("    출력 폴더 경로를 입력하세요 (엔터 시 ./output): ").strip()
                if not output_dir:
                    output_dir = "./output"

                return brief_path, output_dir

      💻 우리 프로젝트에서 어떻게 쓰이나요?

            $ python main.py
            브리프 파일 경로를 입력하세요: brief.json
            출력 폴더 경로를 입력하세요 (엔터 시 ./output):




---
