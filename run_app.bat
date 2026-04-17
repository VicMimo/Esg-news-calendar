@echo off
REM ESG News Calendar — App Streamlit

SET PROJECT_DIR=%~dp0

cd /d "%PROJECT_DIR%"

echo Iniciando ESG News Calendar em http://localhost:8501
python -m streamlit run app/main.py
