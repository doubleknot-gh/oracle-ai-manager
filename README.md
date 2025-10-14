# ⚽ Oracle AI Manager & Coach

우리 축구팀 "Oracle"의 경기 데이터와 선수 프로필을 관리하고, Gemini AI를 통해 경기 리포트, 전술 추천, SNS 홍보 문구를 생성하는 AI 코칭 대시보드 프로젝트입니다.

## 🛠️ 기술 스택

- **Backend**: FastAPI, SQLAlchemy
- **Frontend**: Streamlit
- **Database**: SQLite
- **AI**: Google Gemini API

## 🚀 실행 방법

### 1. 백엔드 서버 실행

```bash
# /backend 폴더로 이동
cd backend

# 라이브러리 설치
pip install -r requirements.txt

# FastAPI 서버 실행
uvicorn app.main:app --reload
```

### 2. 프론트엔드 앱 실행

```bash
# (새 터미널에서) /frontend 폴더로 이동
cd frontend

# 라이브러리 설치
pip install -r requirements.txt

# Streamlit 앱 실행
streamlit run app.py
```