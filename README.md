# AI 브랜드 디자인 생성기 (Brand AI Generator)

브랜드 브리프(업종, 타겟, 키워드 등) 하나만 입력하면, LLM API와 이미지 생성 API를 조합하여
**브랜드 네이밍 · 슬로건 · 브랜드 스토리 · 컬러 팔레트 · 로고 시안**까지 자동으로 생성해주는
CLI 기반 Python 프로그램입니다.

---

## 목차

1. [프로젝트 소개](#1-프로젝트-소개)
2. [과제 목표](#2-과제-목표)
3. [최종 결과물](#3-최종-결과물)
4. [기능 요구사항](#4-기능-요구사항)
5. [에러 처리 가이드](#5-에러-처리-가이드)
6. [개발 환경 설정 (초보자용)](#6-개발-환경-설정-초보자용)
7. [프로젝트 파일 구조](#7-프로젝트-파일-구조)
8. [Git 명령어 정리](#8-git-명령어-정리)
9. [실행 방법](#9-실행-방법)

---

## 1. 프로젝트 소개

브랜드 디자인 외주비가 수백만 원에서 시작하는 이유가 있습니다. 네이밍, 슬로건, 컬러, 로고까지
하나하나가 전문 영역의 작업이기 때문입니다. 브랜드 디자인은 네이밍, 슬로건, 스토리, 컬러,
로고 등 다양한 요소를 종합적으로 기획해야 하는 작업이며, 상당한 시간과 전문성을 요구합니다.

이 프로젝트는 이러한 작업을 **브리프 하나로 자동화**하는 것을 목표로 합니다.

- **LLM API**로 브랜드 네이밍 / 슬로건 / 스토리 / 컬러 팔레트 등 텍스트 기반 브랜드 요소를 생성
- **이미지 생성 API**로 로고 시안을 생성
- 모든 결과물을 지정된 폴더에 JSON과 PNG 형태로 저장

이번 구현에서는 텍스트 생성에 **OpenAI GPT API**, 로고 이미지 생성에 **OpenAI 이미지 생성 API(gpt-image-1)**를
사용합니다.

## 2. 과제 목표

이 과제를 마친 후, 아래 내용을 스스로 설명할 수 있는 것을 목표로 합니다.

| # | 목표 | 이 프로젝트에서 확인할 수 있는 부분 |
|---|---|---|
| 1 | 브랜드 브리프를 입력받아 AI로 브랜드 요소를 생성하는 파이프라인을 설명할 수 있다 | `main.py`의 전체 실행 흐름 (`brief_loader` → `text_generator` → `image_generator` → `result_saver`) |
| 2 | LLM API와 이미지 생성 API를 조합하여 텍스트+이미지 결과물을 생성하는 방법을 설명할 수 있다 | `modules/text_generator.py`(GPT), `modules/image_generator.py`(gpt-image-1) |
| 3 | 생성된 컬러 팔레트를 시각화하여 이미지로 저장하는 방법을 설명할 수 있다 | `modules/palette_visualizer.py` (matplotlib 활용) |
| 4 | API 호출 시 발생할 수 있는 오류 상황과 대응 방법을 설명할 수 있다 | 아래 [5. 에러 처리 가이드](#5-에러-처리-가이드) 표 참고 |

## 3. 최종 결과물

다음 기능이 정상 동작하는 CLI 기반 Python 프로그램 1개를 완성합니다.

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
   - 로고 시안을 PNG 이미지로 저장 (`logo_01.png`, `logo_02.png`, `logo_03.png`)

## 4. 기능 요구사항

| # | 항목 | 상세 내용 | 구현 위치 |
|---|---|---|---|
| 1 | 사용자 입력 | `print`/`input`으로 대화형 입력. 필수: 브리프 파일 경로 / 선택: 출력 폴더 경로(기본값 `./output`) | `main.py: get_user_input()` |
| 2 | 브랜드 브리프 입력 | JSON 파일로 입력. 필수 필드: `industry`, `target`, `keywords` / 선택 필드: `tone`, `competitors`, `notes` | `modules/brief_loader.py` |
| 3 | 브랜드 네이밍 생성 | LLM API로 브랜드명 후보 3~5개 + 의미/유래 설명 생성 | `modules/text_generator.py: generate_naming()` |
| 4 | 슬로건 생성 | LLM API로 톤앤매너에 맞는 슬로건/태그라인 3개 생성 | `modules/text_generator.py: generate_slogans()` |
| 5 | 브랜드 스토리 생성 | LLM API로 탄생 배경/철학/비전을 포함한 300자 내외 스토리 생성 | `modules/text_generator.py: generate_story()` |
| 6 | 컬러 팔레트 생성 | LLM API로 메인 컬러 1개 + 서브 컬러 2~3개(HEX) 추천, matplotlib으로 시각화하여 PNG 저장 | `modules/text_generator.py: generate_color_palette()`, `modules/palette_visualizer.py` |
| 7 | 로고 시안 생성 | 이미지 생성 API(gpt-image-1)로 로고 시안 2~3개 생성 후 PNG 저장 | `modules/image_generator.py` |
| 8 | 결과 저장 | 텍스트 결과는 `brand_result.json`, 이미지는 개별 PNG 파일로 출력 폴더에 저장 | `modules/result_saver.py` |
| 9 | 에러 처리 | API 호출 실패 시 에러 메시지 출력 후 다음 단계 계속 진행 / API 키 오류 시 명확한 안내 메시지 출력 | `modules/config.py`, 각 생성 모듈의 `try/except` |
| 10 | API 키 관리 | API 키를 코드에 직접 작성하지 않고 `.env` 파일(환경변수)에서 읽어옴 | `modules/config.py`, `.env.example` |

## 5. 에러 처리 가이드

과제 목표 4번(*API 호출 시 발생할 수 있는 오류 상황과 대응 방법*)에 해당하는 내용을 정리한 표입니다.
이 프로그램은 **한 단계가 실패해도 전체가 멈추지 않고, 실패한 단계만 건너뛰고 계속 진행**하는 것을
기본 원칙으로 합니다.

| 오류 상황 | 발생 원인 | 프로그램의 대응 | 사용자가 해야 할 일 |
|---|---|---|---|
| **API 키 누락** (`OPENAI_API_KEY` 없음) | `.env` 파일을 만들지 않았거나 환경변수 미설정 | 프로그램 시작 직후 감지하여 안내 메시지 출력 후 **즉시 종료** (`sys.exit(1)`) | `.env` 파일에 `OPENAI_API_KEY=sk-...` 추가 |
| **API 키 인증 실패** (`AuthenticationError`) | 키 값이 잘못되었거나 만료/폐기됨 | 해당 단계(네이밍/슬로건/스토리/컬러/로고)에서 에러 메시지 출력 후 **해당 단계만 건너뛰고 다음 단계 진행** | OpenAI 대시보드에서 키 상태 확인, 새 키 발급 후 `.env` 갱신 |
| **API 요청 한도 초과** (`RateLimitError`) | 짧은 시간에 너무 많은 요청을 보냈거나 사용량 한도 초과 | 에러 메시지 출력 후 해당 단계를 건너뛰고 계속 진행 | 잠시 후 재실행, 또는 OpenAI 요금제/한도 확인 |
| **네트워크 연결 오류** (`APIConnectionError`) | 인터넷 연결 불안정, 방화벽/프록시 차단 | 에러 메시지 출력 후 해당 단계를 건너뛰고 계속 진행 | 네트워크 상태 확인 후 재실행 |
| **OpenAI 서버 오류** (`APIError`, 5xx 등) | OpenAI 서비스 자체의 일시적 장애 | 에러 메시지 출력 후 해당 단계를 건너뛰고 계속 진행 | 잠시 후 재시도, [OpenAI 상태 페이지](https://status.openai.com) 확인 |
| **JSON 파싱 실패** (`JSONDecodeError`) | LLM 응답이 JSON 형식이 아니거나 형식이 깨짐 | 에러 메시지 출력 후 해당 단계 결과를 빈 값으로 처리, 다음 단계 진행 | 재실행 시 대부분 정상 생성됨 (모델 응답 변동성) |
| **브리프 파일 없음/경로 오류** | 사용자가 잘못된 경로 입력 | `[브리프 오류]` 메시지 출력 후 프로그램 종료 | 올바른 파일 경로 재입력 |
| **브리프 JSON 형식 오류** | JSON 문법 오류(콤마 누락 등) | 오류 위치와 함께 메시지 출력 후 프로그램 종료 | JSON 문법 검사 후 재실행 (예: [jsonlint.com](https://jsonlint.com)) |
| **브리프 필수 필드 누락** | `industry`/`target`/`keywords` 중 하나라도 없음 | 누락된 필드명을 출력하고 프로그램 종료 | 브리프 파일에 필수 필드 추가 후 재실행 |
| **로고 이미지 저장 실패** (디스크/권한 문제) | 출력 폴더 쓰기 권한 없음, 디스크 용량 부족 등 | 에러 메시지 출력 후 해당 로고만 건너뛰고 다음 로고 계속 생성 | 출력 폴더 권한/용량 확인 |

> 설계 원칙: 텍스트 생성(2~6번)과 이미지 생성(7번)은 서로 독립적으로 동작하도록 만들어,
> 예를 들어 로고 생성에 실패하더라도 이미 만들어진 네이밍/슬로건/스토리/컬러 결과는
> 정상적으로 `brand_result.json`에 저장됩니다.

## 6. 개발 환경 설정 (초보자용)

Python을 처음 다뤄보는 분도 순서대로 따라 할 수 있도록 단계별로 정리했습니다.

### STEP 1. Python 설치 확인

터미널(명령 프롬프트/PowerShell/터미널 앱)을 열고 아래 명령어로 Python 설치 여부와 버전을 확인합니다.

```bash
python3 --version
# 또는 Windows에서는
python --version
```

`Python 3.9` 이상이면 정상입니다. 설치되어 있지 않다면 [python.org](https://www.python.org/downloads/)에서
설치 파일을 내려받아 설치하세요. (Windows는 설치 시 **"Add Python to PATH"** 체크 필수)

### STEP 2. 프로젝트 폴더로 이동

```bash
cd brand-ai-generator
```

### STEP 3. 가상환경(venv) 생성 및 활성화

가상환경을 쓰면 이 프로젝트에서 설치한 패키지가 컴퓨터의 다른 프로젝트에 영향을 주지 않습니다.

```bash
# 가상환경 생성
python3 -m venv venv

# 가상환경 활성화
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
2. 프로젝트 루트의 `.env.example` 파일을 복사해서 `.env` 파일을 만듭니다.

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

프로그램이 실행되면 브리프 파일 경로(예: `sample_brief.json`)와 출력 폴더 경로를 입력하라는
안내가 나옵니다.

### STEP 7. 가상환경 종료 (작업 종료 시)

```bash
deactivate
```

## 7. 프로젝트 파일 구조

```
brand-ai-generator/
├── main.py                      # CLI 진입점 (전체 실행 흐름 제어)
├── requirements.txt              # 설치가 필요한 패키지 목록
├── .env.example                  # API 키 입력 예시 파일 (실제 키 X)
├── .env                          # 실제 API 키 (직접 생성, Git 추적 제외)
├── .gitignore                    # Git이 추적하지 않을 파일/폴더 목록
├── sample_brief.json             # 테스트용 샘플 브랜드 브리프
├── README.md                     # 프로젝트 설명 문서 (현재 파일)
├── modules/                      # 기능별 모듈 패키지
│   ├── __init__.py
│   ├── config.py                 # API 키 로딩 및 검증
│   ├── brief_loader.py           # 브리프 JSON 로딩/검증
│   ├── text_generator.py         # GPT API: 네이밍/슬로건/스토리/컬러 생성
│   ├── image_generator.py        # gpt-image-1 API: 로고 시안 생성
│   ├── palette_visualizer.py     # matplotlib: 컬러 팔레트 시각화
│   └── result_saver.py           # 최종 결과 JSON 저장
└── output/                       # 실행 결과물이 저장되는 폴더 (자동 생성)
    ├── brand_result.json
    ├── color_palette.png
    ├── logo_01.png
    ├── logo_02.png
    └── logo_03.png
```

## 8. Git 명령어 정리

버전 관리를 처음 해보는 분들을 위한 기본 Git 명령어 흐름입니다.

| 단계 | 명령어 | 설명 |
|---|---|---|
| Git 설치 확인 | `git --version` | 설치되어 있지 않다면 [git-scm.com](https://git-scm.com/)에서 설치 |
| 사용자 정보 최초 설정 | `git config --global user.name "이름"` `git config --global user.email "이메일"` | 최초 1회만 설정하면 됨 |
| 저장소 초기화 | `git init` | 프로젝트 폴더를 Git 저장소로 만듦 |
| 변경 사항 확인 | `git status` | 어떤 파일이 추가/수정/삭제되었는지 확인 |
| 스테이징 | `git add .` | 모든 변경 파일을 커밋 대상으로 등록 (`.env`는 `.gitignore`로 제외됨) |
| 커밋 | `git commit -m "커밋 메시지"` | 스테이징된 변경 사항을 저장 |
| 원격 저장소 연결 | `git remote add origin <저장소_URL>` | GitHub 등 원격 저장소와 연결 (최초 1회) |
| 원격 저장소로 업로드 | `git push origin main` | 로컬 커밋을 원격 저장소로 전송 |
| 원격 저장소에서 내려받기 | `git pull origin main` | 원격 저장소의 최신 변경 사항을 받아옴 |
| 브랜치 생성/이동 | `git checkout -b feature/기능이름` | 새 기능 개발용 브랜치 생성 및 이동 |
| 커밋 로그 확인 | `git log --oneline` | 지금까지의 커밋 이력을 한 줄씩 확인 |

### 처음 GitHub에 업로드하는 전체 흐름 예시

```bash
git init
git add .
git commit -m "Initial commit: 브랜드 AI 생성기 프로젝트 구조 작성"
git branch -M main
git remote add origin https://github.com/사용자명/brand-ai-generator.git
git push -u origin main
```

## 9. 실행 방법

```bash
# 1) 가상환경 활성화 (STEP 3 참고)
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

> API 호출이 실패하는 단계가 있어도(예: 네트워크 오류, 키 인증 실패 등) 해당 단계의 실패
> 메시지만 출력되고 나머지 단계는 계속 진행됩니다. 자세한 내용은 [5. 에러 처리 가이드](#5-에러-처리-가이드)를 참고하세요.

실행이 끝나면 `output/` 폴더(또는 직접 지정한 폴더)에 아래 파일들이 생성됩니다.

- `brand_result.json` — 네이밍, 슬로건, 스토리, 컬러 정보, 생성된 파일 목록
- `color_palette.png` — 컬러 팔레트 시각화 이미지
- `logo_01.png`, `logo_02.png`, `logo_03.png` — AI가 생성한 로고 시안
