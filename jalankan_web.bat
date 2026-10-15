@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>&1
if not errorlevel 1 (
    start "Sahabat Sehat - Web Server" cmd /k "cd /d ""%~dp0"" && py -3 web_app.py"
) else (
    where python >nul 2>&1
    if errorlevel 1 (
        echo Python tidak ditemukan. Install Python atau tambahkan ke PATH.
        pause
        exit /b 1
    )
    start "Sahabat Sehat - Web Server" cmd /k "cd /d ""%~dp0"" && python web_app.py"
)

powershell -NoProfile -ExecutionPolicy Bypass -Command "$url='http://127.0.0.1:8000/'; for ($i=0; $i -lt 30; $i++) { try { $response=Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 1; if ($response.StatusCode -eq 200) { Start-Process $url; exit 0 } } catch { }; Start-Sleep -Milliseconds 500 }; exit 1"
if errorlevel 1 (
    echo Server belum siap. Periksa jendela server untuk melihat pesan error.
    pause
    exit /b 1
)

echo Sahabat Sehat telah dibuka di browser.
exit /b 0
