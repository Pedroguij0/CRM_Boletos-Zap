import os
import sys
import shutil
import webbrowser
from threading import Timer

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

env_path = os.path.join(BASE_DIR, '.env')
if os.path.exists(env_path):
    with open(env_path, 'r', encoding="utf-8") as f:
        for linha in f:
            linha = linha.strip()
            if linha and not linha.startswith("#"):
                chave, valor = linha.split("=", 1)
                os.environ[chave.strip()] = valor.strip().strip('"').strip("'")

from app import create_app
app = create_app()

def abrir_navegador():
    if sys.platform == 'win32':
        os.system('start http://127.0.0.1:5000/')
    else:
        webbrowser.open("http://127.0.0.1:5000/")

if __name__ == '__main__':
    # Realizar backup de segurança do banco local de forma automática no Python
    database_file = os.path.join(BASE_DIR, "Dados_Boletos.db")
    print("Servidor Flask carregado com sucesso!")
    print("Acesse as telas pelo navegador em: http://127.0.0.1:5000/")
    
    # Inicia a thread para abrir o navegador automaticamente após 1.5s
    Timer(1.5, abrir_navegador).start()
    
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
