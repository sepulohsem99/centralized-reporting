@echo off
REM ===================================================================
REM  LAPORAN BERPUSAT - PUBLISH
REM
REM  1. Jana semula folder public/ (statik)
REM  2. Commit + push ke GitHub (backup kod)
REM  3. Deploy public/ ke Cloudflare Pages (wrangler direct upload)
REM
REM  Perlu: fail .cf_token dalam folder ini (API token Cloudflare).
REM ===================================================================
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo.
echo [1/3] Menjana public/ ...
python jana_statik.py
if errorlevel 1 ( echo [GAGAL] jana_statik.py & endlocal & exit /b 1 )

echo.
echo [2/3] Commit + push GitHub ...
if exist ".git" (
  git add -A
  git diff --cached --quiet || git commit -m "Laporan berpusat: kemaskini"
  git push
) else (
  echo [INFO]  Belum repo git - langkau push. Jalankan pasang_repo.py dahulu.
)

echo.
echo [3/3] Deploy ke Cloudflare Pages ...
if not exist ".cf_token" (
  echo [GAGAL] fail .cf_token tiada - simpan API token Cloudflare ke dalamnya.
  endlocal & exit /b 1
)
set /p CLOUDFLARE_API_TOKEN=<.cf_token
npx --yes wrangler pages deploy public --project-name=centralized-reporting --commit-dirty=true
if errorlevel 1 ( echo [GAGAL] wrangler deploy & endlocal & exit /b 1 )

echo.
echo ================================================================
echo   SIAP. Live: https://centralized-reporting.pages.dev
echo ================================================================
endlocal
exit /b 0
