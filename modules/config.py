"""
config.py
---------
환경 변수(.env) 또는 환경변수에서 API 키를 읽어오는 모듈.
요구사항 10번: API 키를 코드에 직접 작성하지 않고 환경변수/설정 파일에서 읽어온다.
"""

import os
import sys

try:
    from dotenv import load_dotenv
    load_dotenv()  # 프로젝트 루트의 .env 파일을 자동으로 읽어 환경변수로 등록
except ImportError:
    # python-dotenv가 설치되지 않았어도 실제 환경변수만으로 동작할 수 있게 예외 처리
    pass


class ConfigError(Exception):
    """설정(API 키 등) 관련 오류를 나타내는 예외"""
    pass


def get_openai_api_key() -> str:
    """
    OPENAI_API_KEY 환경변수를 읽어 반환한다.
    값이 없거나 형식이 이상하면 사용자에게 명확한 안내 메시지를 출력하고 프로그램을 종료한다.
    (요구사항 9번: API 키가 없거나 잘못된 경우 명확한 안내 메시지를 출력한다.)
    """
    api_key = os.getenv("OPENAI_API_KEY", "").strip()

    if not api_key:
        print("\n[설정 오류] OPENAI_API_KEY가 설정되어 있지 않습니다.")
        print("다음 방법 중 하나로 API 키를 설정해주세요.")
        print("  1) 프로젝트 루트에 .env 파일을 만들고 아래처럼 작성:")
        print("     OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx")
        print("  2) 터미널에서 환경변수로 직접 설정:")
        print("     (macOS/Linux) export OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx")
        print("     (Windows PowerShell) $env:OPENAI_API_KEY=\"sk-xxxxxxxxxxxxxxxx\"")
        sys.exit(1)

    if not api_key.startswith("sk-"):
        print("\n[설정 경고] OPENAI_API_KEY 형식이 올바르지 않은 것 같습니다.")
        print("OpenAI API 키는 보통 'sk-'로 시작합니다. 키 값을 다시 확인해주세요.")
        # 형식 경고만 하고 실행은 계속 진행 (실제 유효성은 API 호출 시 판별됨)

    return api_key
