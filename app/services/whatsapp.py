from app.models import Configuracao
import os
import requests

def enviar_mensagem(session, telefone, nome, valor, vencimento, parcela_atual, total_parcelas, codigo_id, template_nome):
    config = session.query(Configuracao).first()
    token_meta = config.meta_token or os.getenv('META_TOKEN')
    phone_id = config.phone_number_id or os.getenv('META_PHONE_ID')
    url = f"https://graph.facebook.com/v18.0/{phone_id}/messages"
    headers ={
        "Authorization":f"Bearer {token_meta}",
        "Content-Type":"application/json"
    }
    payload ={
        "messaging_product": "whatsapp",
        "to":telefone,
        "type":"template",
        "template":{
            "name":template_nome,
            "language":{
                "code":"pt-BR"
            },
            "components":[
                {
                    "type":"body",
                    "parameters":[
                        {"type":"text", "text":nome},
                        {"type":"text", "text":f"{valor:.2f}"},
                        {"type":"text", "text":vencimento.strftime("%d/%m/%Y")},
                        {"type":"text", "text":str(parcela_atual)},
                        {"type":"text", "text":str(total_parcelas)},
                        {"type":"text", "text":str(codigo_id)}
                    ]
                }
            ]
        }
    }
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        dados_resposta = response.json()
        if response.status_code == 200:
            message_id = dados_resposta["messages"][0]["id"]
            return True, message_id
        else:
            erro_envio = dados_resposta.get("error", {}).get("message", "Erro desconhecido")
            return False, f"Meta API Erro({response.status_code}): {erro_envio}"
    except Exception as e:
        return False, f"Erro de conexão com a META: {str(e)}"

        