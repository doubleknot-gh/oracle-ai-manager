import os
from dotenv import load_dotenv # 임시로 주석 처리
import google.generativeai as genai

# .env 파일에서 환경 변수 로드
# main.py에서 uvicorn으로 실행될 때의 현재 작업 디렉토리는 backend/ 입니다.
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("오류: GEMINI_API_KEY가 .env 파일에 설정되지 않았습니다.")
else:
    genai.configure(api_key=GEMINI_API_KEY)
    print("✅ 사용 가능한 Gemini 모델 리스트:")
    print("-" * 40)
    
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"  - {m.name}")
    except Exception as e:
        print(f"모델 리스트를 불러오는 중 오류가 발생했습니다: {e}")