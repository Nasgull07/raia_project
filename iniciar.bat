@echo off
echo ========================================
echo   Iniciando Proyecto OCR
echo ========================================
echo.

echo [1/2] Iniciando API FastAPI...
echo.
start cmd /k "cd FastAPI && echo Iniciando FastAPI... && uvicorn main:app --reload"

timeout /t 5 /nobreak >nul

echo [2/2] Iniciando Interfaz Streamlit...
echo.
start cmd /k "cd UI && echo Iniciando Streamlit... && streamlit run streamlit_app.py"

echo.
echo ========================================
echo   Proyecto iniciado!
echo ========================================
echo.
echo API: http://localhost:8000
echo UI:  Se abrira automaticamente
echo.
echo Presiona cualquier tecla para salir...
pause >nul
