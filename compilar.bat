@echo off
title CRM BoletosZap - Compilador PyInstaller
color 05
cls
echo ======================================================================
echo                  COMPILANDO PROGRAMA COM PYINSTALLER
echo ======================================================================
echo.
echo [1/2] Limpando pastas temporarias antigas...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist CRM_BoletosZap.spec del /q CRM_BoletosZap.spec
echo [OK] Pastas limpas.
echo.

echo [2/2] Compilando executavel unico...
echo Isso pode levar de 1 a 2 minutos. Por favor, aguarde...
echo.

:: Configura o PATH incluindo os binários do Anaconda para puxar DLLs de sistema necessárias
set Path=C:\Users\allme\Downloads\Escola\Anaconda\Library\bin;C:\Users\allme\Downloads\Escola\Anaconda\DLLs;C:\Users\allme\Downloads\Escola\Anaconda;%Path%

:: Roda a compilação a partir do ambiente virtual limpo (.venv)
.venv\Scripts\pyinstaller --noconfirm --onefile --console --name "CRM_BoletosZap" --add-data "app/templates;app/templates" --add-data "app/static;app/static" run.py

echo.
echo ======================================================================
if exist dist\CRM_BoletosZap.exe (
    echo [SUCESSO] O arquivo executavel foi gerado com exito!
    echo Ele se encontra em: dist\CRM_BoletosZap.exe
    echo.
    echo Você pode enviar apenas o arquivo dist\CRM_BoletosZap.exe
    echo para o seu cliente. Quando ele clicar, o banco de dados
    echo e as pastas de backup/logs serao criadas na mesma pasta dele!
) else (
    echo [ERRO] Houve uma falha durante o processo de compilacao.
)
echo ======================================================================
echo.
pause
