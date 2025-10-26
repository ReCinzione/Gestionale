@echo off
echo ========================================
echo    GESTIONALE NEGOZIO - AVVIO
echo ========================================
echo.

REM Cambia nella directory dello script
cd /d "%~dp0"

echo Ricerca Python...

REM Prova a trovare il percorso di Python usando py
for /f "tokens=*" %%i in ('py -c "import sys; print(sys.executable)" 2^>nul') do set PYTHON_PATH=%%i

if defined PYTHON_PATH (
    echo Python trovato: %PYTHON_PATH%
    echo Avvio applicazione...
    echo.
    "%PYTHON_PATH%" main.py
    goto :end
)

echo.
echo Tentativo con 'py' diretto...
py --version >nul 2>&1
if %errorlevel% == 0 (
    echo Python trovato con 'py'! Tentativo avvio...
    py main.py
    if %errorlevel% == 0 goto :end
)

echo.
echo Tentativo con 'python' diretto...
python --version >nul 2>&1
if %errorlevel% == 0 (
    echo Python trovato! Tentativo avvio...
    python main.py
    if %errorlevel% == 0 goto :end
)

REM Prova percorsi comuni di Python
echo.
echo Ricerca in percorsi comuni...

set "COMMON_PATHS=C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\python.exe"
set "COMMON_PATHS=%COMMON_PATHS% C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python310\python.exe"
set "COMMON_PATHS=%COMMON_PATHS% C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python39\python.exe"
set "COMMON_PATHS=%COMMON_PATHS% C:\Python311\python.exe"
set "COMMON_PATHS=%COMMON_PATHS% C:\Python310\python.exe"

for %%p in (%COMMON_PATHS%) do (
    if exist "%%p" (
        echo Python trovato in: %%p
        echo Avvio applicazione...
        echo.
        "%%p" main.py
        goto :end
    )
)

echo.
echo ========================================
echo   ERRORE: Python non trovato!
echo ========================================
echo.
echo Soluzioni:
echo 1. Installa Python da: https://www.python.org/downloads/
echo 2. Durante l'installazione, spunta "Add Python to PATH"
echo 3. Riavvia il computer dopo l'installazione
echo 4. Disabilita alias Python in Windows:
echo    - Impostazioni ^> App ^> Alias di esecuzione app
echo    - Disabilita "python.exe" e "python3.exe"
echo.

:end
echo.
echo Premi un tasto per chiudere...
pause >nul
