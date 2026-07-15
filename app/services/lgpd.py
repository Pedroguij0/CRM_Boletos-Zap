import os
import json
from datetime import datetime, date

LOG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "logs"))
LOG_FILE = os.path.join(LOG_DIR, "auditoria_meta.json")

def registrar_log(acao, status, detalhes):
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    entrada_log ={
        "data_hora":datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "acao":acao,
        "status":status,
        "detalhes":detalhes
    }

    logs=[]
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                logs = json.load(f)
        except Exception:
            logs = []
    logs.insert(0, entrada_log)
    try:
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Erro ao salvar log: {e}")
