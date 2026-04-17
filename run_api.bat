@echo off
REM ESG News Calendar — API FastAPI

SET PROJECT_DIR=%~dp0

cd /d "%PROJECT_DIR%"

echo Iniciando ESG News API em http://localhost:8000
echo Documentacao: http://localhost:8000/docs
echo Pressione Ctrl+C para encerrar.

python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
