@echo off
echo ========================================
echo   INSTALLAZIONE TESSERACT OCR
echo ========================================
echo.

echo Questo script ti aiutera' a installare Tesseract OCR
echo per l'estrazione automatica dati dalle fatture.
echo.

echo ATTENZIONE: Serve connessione internet per il download.
echo.

pause

echo.
echo Apertura pagina download Tesseract...
echo.

REM Apri la pagina di download
start https://github.com/UB-Mannheim/tesseract/wiki

echo.
echo ========================================
echo   ISTRUZIONI INSTALLAZIONE
echo ========================================
echo.
echo 1. Nella pagina che si e' aperta, cerca:
echo    "tesseract-ocr-w64-setup-5.x.x.exe"
echo.
echo 2. Scarica il file (circa 60 MB)
echo.
echo 3. Esegui il file come AMMINISTRATORE
echo.
echo 4. Durante l'installazione:
echo    - Percorso: C:\Program Files\Tesseract-OCR
echo    - IMPORTANTE: Spunta "Italian language pack"
echo.
echo 5. Completa l'installazione
echo.
echo 6. Riavvia l'applicazione gestionale
echo.
echo 7. Ora i PDF estrarranno automaticamente i dati!
echo.

echo ========================================
echo   VERIFICA INSTALLAZIONE
echo ========================================
echo.

REM Controlla se Tesseract è già installato
if exist "C:\Program Files\Tesseract-OCR\tesseract.exe" (
    echo ✓ Tesseract GIA' INSTALLATO in:
    echo   C:\Program Files\Tesseract-OCR\tesseract.exe
    echo.
    echo L'OCR dovrebbe funzionare nell'applicazione!
    echo Se non funziona, riavvia l'applicazione.
) else (
    echo ✗ Tesseract NON ancora installato
    echo   Segui le istruzioni sopra per installarlo
)

echo.
echo Premi un tasto per chiudere...
pause >nul
