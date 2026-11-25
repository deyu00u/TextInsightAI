@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Copy these update files into your existing TextInsightAI folder first.
  pause
  exit /b 1
)
.venv\Scripts\python.exe -m pip install -r requirements-local.txt
if errorlevel 1 (
  echo Installation failed. Please copy the error message.
  pause
  exit /b 1
)
.venv\Scripts\python.exe -m streamlit run app.py
pause
