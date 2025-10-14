import os
import google.generativeai as genai

# .env 파일에서 환경 변수 로드
# main.py에서 uvicorn으로 실행될 때의 현재 작업 디렉토리는 backend/ 입니다.

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")

genai.configure(api_key=GEMINI_API_KEY)

# 사용 가능한 모델 리스트에 있는 'gemini-flash-latest' 모델로 변경합니다.
model = genai.GenerativeModel('gemini-flash-latest')

def generate_text_from_gemini(prompt: str) -> str:
    """Gemini API를 호출하여 텍스트를 생성합니다."""
    response = model.generate_content(prompt)
    return response.text