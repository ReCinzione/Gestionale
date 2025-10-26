@echo off
echo ========================================
echo   INSTALLAZIONE DIPENDENZE
echo ========================================
echo.

REM Cambia nella directory dello script
cd /d "%~dp0"

echo Ricerca Python...

REM Prova a trovare il percorso di Python usando py
for /f "tokens=*" %%i in ('py -c "import sys; print(sys.executable)" 2^>nul') do set PYTHON_PATH=%%i

if defined PYTHON_PATH (
    echo Python trovato: %PYTHON_PATH%
    echo Installazione dipendenze...
    echo.
    "%PYTHON_PATH%" -m pip install -r requirements.txt
    echo.
    echo ========================================
    echo   INSTALLAZIONE COMPLETATA!
    echo ========================================
    echo.
    echo Ora puoi avviare l'applicazione con:
    echo - Doppio click su "avvia_gestionale.bat"
    echo.
    goto :end
)

echo.
echo Controllo Python con 'py'...
py --version >nul 2>&1
if %errorlevel% == 0 (
    echo Python trovato con 'py'! Installazione dipendenze...
    py -m pip install -r requirements.txt
    echo.
    echo ========================================
    echo   INSTALLAZIONE COMPLETATA!
    echo ========================================
    echo.
    echo Ora puoi avviare l'applicazione con:
    echo - Doppio click su "avvia_gestionale.bat"
    echo.
    goto :end
)

echo.
echo Tentativo con 'py'...
py --version >nul 2>&1
if %errorlevel% == 0 (
    echo Python trovato con 'py'! Installazione dipendenze...
    py -m pip install -r requirements.txt
    echo.
    echo ========================================
    echo   INSTALLAZIONE COMPLETATA!
    echo ========================================
    echo.
    echo Ora puoi avviare l'applicazione con:
    echo - Doppio click su "avvia_gestionale.bat"
    echo - Oppure: py main.py
    echo.
    goto :end
)

echo.
echo ========================================
echo   ERRORE: Python non trovato!
echo ========================================
echo.
echo Prima di installare le dipendenze, devi installare Python:
echo.
echo 1. Vai su: https://www.python.org/downloads/
echo 2. Scarica Python 3.8 o superiore
echo 3. Durante l'installazione, spunta "Add Python to PATH"
echo 4. Riavvia il computer
echo 5. Rilancia questo file
echo.

:end
echo.
echo Premi un tasto per chiudere...
pause >nul
