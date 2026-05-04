@echo off
echo Cleaning up old venvs - keeping WorkBook only...
rmdir /s /q "C:\Users\manoj\.venv"
rmdir /s /q "C:\Users\manoj\ConsolidatedProjects\indusvision-dashboard\venv"
rmdir /s /q "C:\Users\manoj\ConsolidatedProjects\ollama-code-pilot-manoj548\.venv"
echo Cleanup complete. WorkBook preserved.
pause
