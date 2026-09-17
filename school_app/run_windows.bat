@echo off
chcp 65001 >nul
echo ================================================
echo   MAKTAB PLATFORMASI - Lokal test
echo ================================================
echo.
echo Flask o'rnatilmoqda...
pip install flask
echo.
echo Ilova ishga tushmoqda...
echo.
echo Login: admin
echo Parol: admin123
echo.
echo Brauzerda oching: http://127.0.0.1:5000
echo.
echo To'xtatish: Ctrl+C
echo ================================================
echo.
python run.py
pause
