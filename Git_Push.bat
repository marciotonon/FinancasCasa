@echo off
setlocal
cd /d %~dp0

set "msg=%~1"
if "%msg%"=="" set /p msg=Mensagem do commit: 

if "%msg%"=="" (
    echo Mensagem do commit obrigatoria.
    exit /b 1
)

git add -A
git diff --cached --quiet
if not errorlevel 1 (
    echo Nenhuma mudanca para enviar.
    exit /b 0
)

git pull --rebase --autostash origin main
if errorlevel 1 (
    echo.
    echo Falha no pull antes do push.
    exit /b 1
)

git commit -m "%msg%"
if errorlevel 1 (
    echo.
    echo Falha ao criar o commit.
    exit /b 1
)

git push origin main
if errorlevel 1 (
    echo.
    echo Falha ao enviar para o GitHub.
    exit /b 1
)

echo.
echo Push concluido com sucesso.
