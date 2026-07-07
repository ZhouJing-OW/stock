@echo off
cd /d "E:\Hanako_WorkSpace\研报\个股研究"

:: Add Git to PATH
set "PATH=C:\Program Files\Git\cmd;%PATH%"

echo ========================================
echo  Stock Research DB Sync to GitHub
echo ========================================
echo.

echo [1/3] Refreshing index...
python bridge\scan_index.py
if errorlevel 1 (
    echo [ERROR] Index refresh failed!
    pause
    exit /b 1
)
echo.

echo [2/3] Committing changes...
git add -A
set /p msg="Commit message (Enter=default): "
if "%msg%"=="" set msg=Data update %date%
git commit -m "%msg%"
echo.

echo [3/3] Pushing to GitHub...
git push -u origin main
echo.
echo ========================================
echo  Sync complete!
echo ========================================
pause
