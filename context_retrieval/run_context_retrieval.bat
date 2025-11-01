@echo off
REM Context Retrieval Service Launcher
REM This script launches the context retrieval service from any directory

echo ========================================
echo Context Retrieval Service
echo ========================================
echo.
echo Starting service...
echo Press Ctrl+C to stop
echo.

REM Change to the parent directory (project root)
cd /d "%~dp0\.."

REM Run the context retrieval service
python context_retrieval/ContextRetrievalService.py

pause

