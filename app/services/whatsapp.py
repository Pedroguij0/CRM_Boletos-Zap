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

    # Ajusta dinamicamente a quantidade de parâmetros e o idioma de acordo com o template
    parameters = []
    language_code = "pt_BR"

    if template_nome == "jaspers_market_order_confirmation_v1":
        language_code = "en_US"
        parameters = [
            {"type": "text", "text": nome},
            {"type": "text", "text": str(codigo_id)},
            {"type": "text", "text": vencimento.strftime("%d/%m/%Y")}
        ]
    elif template_nome == "jaspers_market_plain_text_v1" or template_nome == "hello_world":
        language_code = "en_US"
        parameters = []
    else:
        # Padrão para boleto_automatico_v2 (6 variáveis)
        language_code = "pt_BR"
        parameters = [
            {"type":"text", "text":nome},
            {"type":"text", "text":f"{valor:.2f}"},
            {"type":"text", "text":vencimento.strftime("%d/%m/%Y")},
            {"type":"text", "text":str(parcela_atual)},
            {"type":"text", "text":str(total_parcelas)},
            {"type":"text", "text":str(codigo_id)}
        ]

    payload = {
        "messaging_product": "whatsapp",
        "to": telefone,
        "type": "template",
        "template": {
            "name": template_nome,
            "language": {
                "code": language_code
            }
        }
    }

    if parameters:
        payload["template"]["components"] = [
            {
                "type": "body",
                "parameters": parameters
            }
        ]
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

def gerar_texto_template(template_nome, nome, valor, vencimento, parcela_atual, total_parcelas, codigo_id):
    venc_str = vencimento.strftime("%d/%m/%Y") if hasattr(vencimento, "strftime") else str(vencimento)
    if template_nome == "boleto_automatico_v2":
        return f"Olá {nome}, informamos que o boleto no valor de R$ {valor:.2f}, com vencimento em {venc_str}, referente à parcela {parcela_atual}/{total_parcelas} está disponível. Segue o código de barras para pagamento: {codigo_id}"
    elif template_nome == "jaspers_market_order_confirmation_v1":
        return f"Hi {nome},\n\nThank you for your purchase! Your order number is {codigo_id}.\n\nWe'll start getting your farm fresh groceries ready to ship.\n\nEstimated delivery: {venc_str}."
    elif template_nome == "jaspers_market_plain_text_v1":
        return "Welcome to Jasper’s Market, your local grocery store providing farm-fresh produce and high-quality goods!"
    elif template_nome == "hello_world":
        return f"Olá {nome}, informamos que o boleto no valor de R$ {valor:.2f}, com vencimento em {venc_str}, referente à parcela {parcela_atual}/{total_parcelas} está disponível. Segue o código de barras para pagamento: {codigo_id}"
    else:
        return f"Cobrança enviada usando o template {template_nome}. Valor: R$ {valor:.2f}"