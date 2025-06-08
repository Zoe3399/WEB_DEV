@REM 가상환경 재재설정 스크립트
REM 이 스크립트는 Windows 환경에서 실행됩니다.

@echo off
echo ==== 1. 기존 .venv 폴더 삭제 ====
rmdir /s /q .venv

echo ==== 2. 새 가상환경(.venv) 생성 ====
python -m venv .venv

echo ==== 3. 가상환경 활성화 ====
call .venv\Scripts\activate

echo ==== 4. pip 업그레이드 ====
python -m pip install --upgrade pip

echo ==== 5. 주요 패키지 설치 ====
pip install --upgrade setuptools wheel
pip install streamlit pandas sqlalchemy bcrypt xlsxwriter

echo ==== 6. 설치 패키지 목록 ====
pip list

echo ==== 가상환경 준비 완료! ====
pause

echo === 7. 패키지 설치 ===
pip install -r requirements.txt
