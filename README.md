# 1) .venv 라는 이름으로 가상환경 새로 생성
python -m venv .venv

# 2) 새로 만든 가상환경에 패키지 설치
. \.venv\Scripts\pip.exe install -r .\requirements.txt

# 3) backend 실행
cd backend
. \.venv\Scripts\python.exe -m app.main

# 4) frontend 실행
cd frontend
npm run dev