import os
if os.path.exists('.env'):
    with open(".env",'r',encoding="utf-8") as f:
        for linha in f:
            linha = linha.strip()
            if linha and not linha.startswith("#"):
                chave,valor = linha.split("=",1)
                os.environ[chave.strip()] = valor.strip().strip('"').strip("'")
                
from app import create_app
app = create_app()
if __name__ == '__main__':
    print("Servidor Flask carregado com sucesso!")
    print("Acesse as telas pelo navegador em: http://127.0.0.1:5000/")
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
