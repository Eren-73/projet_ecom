@echo off
cd /d %~dp0
set /p message="Message de commit : "

git add .
git commit -m "%message%"
git push origin master

echo.
echo ✔ Code envoyé sur GitHub avec succès !
pause