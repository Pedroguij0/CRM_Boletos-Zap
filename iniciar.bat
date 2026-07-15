@echo off
title CRM BoletosZap - Inicializador Automático
color 0b
cls
echo ======================================================================
echo                     INICIALIZADOR DO CRM BOLETOSZAP
echo ======================================================================
echo.

:: 1. Criar pasta de backups caso não exista
echo [1/3] Criando backup de seguranca do banco de dados...
if not exist backups mkdir backups
if exist Dados_Boletos.db (
    copy Dados_Boletos.db backups\Dados_Boletos_Backup.db /Y >nul
    echo [OK] Backup criado em: backups\Dados_Boletos_Backup.db
) else (
    echo [AVISO] Banco de dados inicial nao encontrado. Sera criado automaticamente.
)
echo.

:: 2. Abrir o navegador padrão em background após 3 segundos
echo [2/3] Preparando para abrir o painel do navegador...
start "" "http://127.0.0.1:5000/"

:: 3. Iniciar o servidor Flask
echo [3/3] Iniciando o servidor Flask em segundo plano...
echo.
echo ----------------------------------------------------------------------
echo Pressione CTRL+C nesta janela preta para desligar o sistema.
echo ----------------------------------------------------------------------
echo.

:: Tenta localizar e usar a instalação do Python do Anaconda do usuário
set env_path="C:\Users\allme\Downloads\Escola\Anaconda;C:\Users\allme\Downloads\Escola\Anaconda\Scripts;"
set Path=%env_path%%Path%

python run.py
pause
