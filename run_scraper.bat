@echo off
REM ESG News Calendar — Scraper Diario
REM Configure no Agendador de Tarefas do Windows para rodar todo dia as 08:00

SET PROJECT_DIR=%~dp0

cd /d "%PROJECT_DIR%"

IF NOT EXIST logs mkdir logs

python -m scraper.pipeline >> "%PROJECT_DIR%logs\scraper_%date:~-4,4%%date:~-7,2%%date:~-10,2%.log" 2>&1

echo %date% %time% - Scraper finalizado >> "%PROJECT_DIR%logs\run_history.log"
