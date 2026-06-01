@echo off
setlocal
cd /d %~dp0
git pull --rebase --autostash origin main
if errorlevel 1 (
    echo.
    echo Falha ao atualizar o repositorio.
    exit /b 1
)
echo.
echo Repositorio atualizado com sucesso.
