from app.services.whatsapp import enviar_mensagem, gerar_texto_template
from flask import Blueprint, jsonify, request, send_file
import os
import json
import io
from datetime import datetime
from werkzeug.utils import secure_filename
from app.db import get_session
from app.models import Titular, Boleto, Configuracao, Mensagem
from app.services.import_services import importar_clientes, importar_boletos
from app.services.boleto_service import registrar_pagamento
from app.services.lgpd import LOG_FILE, registrar_log

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/clientes', methods = ['GET'])
def listar_clientes():
    session = get_session()
    try:
        clientes = session.query(Titular).order_by(Titular.nome).all()
        return jsonify([{
            "id":c.id,
            "codcli":c.codcli,
            "nome": c.nome,
            "notificacao_ativa": c.notificacao_ativa,
            "telefone": c.telefone
        }for c in clientes]), 200
    except Exception as e:
        return jsonify({"erro":str(e)}),500
    finally:
        session.close()

@api_bp.route('/clientes/<int:cliente_id>/notificacao', methods=["PUT"])
def alterar_notificacao(cliente_id):
    session = get_session()
    dados = request.get_json()
    if not dados or 'notificacao_ativa' not in dados:
        return jsonify({"erro" :"O parametro 'notificacao_ativa' nao foi encontrado" }), 400

    try:
        cliente = session.query(Titular).filter(Titular.id == cliente_id).first()
        if not cliente:
            return jsonify({f"erro": "O cliente de id {cliente_id} nao foi encontrado"}), 404
        cliente.notificacao_ativa = bool(dados['notificacao_ativa'])
        session.commit()
        return jsonify({'mensagem':'status de notificacao alterado com sucesso!'}), 200
    except Exception as e:
        session.rollback()
        return jsonify({'erro':str(e)}),500
    finally:
        session.close()

@api_bp.route('/boletos', methods=["GET"])
def listar_boletos():
    session = get_session()
    try:
        boletos= session.query(Boleto).order_by(Boleto.data_vencimento.asc()).all()
        listaB = []
        for b in boletos:
            titular = session.query(Titular).filter(Titular.id == b.titular_id).first()
            listaB.append({
                "id":b.id,
                "cliente_nome": titular.nome if titular else "Cliente nao identificado",
                "codigo_id": b.codigo_id,
                "valor":b.valor,
                "data de vencimento": b.data_vencimento,
                "parcela_atual":b.parcela_atual,
                "total_parcelas":b.total_parcelas,
                "status":b.status                
            })
        return jsonify(listaB), 200
    except Exception as e:
        return jsonify({"erro":str(e)}),500
    finally:
        session.close()

@api_bp.route("/boletos/<int:boleto_id>/pagar", methods=["POST"])
def liquidar_boleto(boleto_id):
    session = get_session()
    dados = request.get_json() or {}
    data_pagamento_str = dados.get('data_pagamento')
    data_pagamento = None
    if data_pagamento_str:
        try:
            data_pagamento = datetime.strptime(data_pagamento_str, "%d-%m-%Y").date()
        except ValueError:
            return jsonify({"erro":"Formato de data invalido. use DD-MM-YYYY"}), 400
    try:
        sucesso,msg = registrar_pagamento(session, boleto_id, data_pagamento)
        if sucesso:
            return jsonify({"mensagem:": msg}), 200
        return jsonify({"erro":msg}), 400
    except Exception as e:
        return jsonify({"erro":str(e)}), 500
    finally:
        session.close()

@api_bp.route("/import", methods=["POST"])
def importar_planilha():
    session = get_session()
    file_clientes = request.files.get('clientes')
    file_boletos = request.files.get('boletos')
    if not file_clientes and not file_boletos:
        return jsonify({"erro":"Envie pelo menos um arquivo excel com os dados dos Clientes e Boletos"}),400
    from app.config import TEMP_DIR as temp_dir
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    clientes_novos = 0
    boletos_novos = 0
    try:
        if file_clientes:
            file_path= os.path.join(temp_dir, secure_filename(file_clientes.filename))
            file_clientes.save(file_path)
            clientes_novos = importar_clientes(session, file_path)
            os.remove(file_path)
        if file_boletos:
            file_path = os.path.join(temp_dir, secure_filename(file_boletos.filename))
            file_boletos.save(file_path)
            boletos_novos = importar_boletos(session, file_path)
            os.remove(file_path)
        return jsonify({
            "Clientes Cadastrados": clientes_novos,
            "Boletos Cadastrados": boletos_novos
        }), 200
    except Exception as e:
        return jsonify({'erro':str(e)}),500
    finally:
        session.close()

@api_bp.route("/config", methods=['GET',"POST"])
def gerenciar_config():
    session = get_session()
    config = session.query(Configuracao).first()
    if not config:
        config = Configuracao()
        session.add(config)
        session.commit()
    if request.method == 'GET':
        return jsonify({
            "dias_antecedencia":config.dias_antecedencia,
            "template_nome":config.template_nome,
            "horario_envio":config.horario_envio,
            "verify_token":config.verify_token,
            "meta_token":config.meta_token,
            "phone_number_id":config.phone_number_id

        }),200
    dados = request.get_json()
    try:
        config.dias_antecedencia = int(dados.get('dias_antecedencia', config.dias_antecedencia))
        config.template_nome = str(dados.get('template_nome', config.template_nome))
        config.horario_envio = str(dados.get("horario_envio", config.horario_envio))
        config.meta_token = dados.get('meta_token',config.meta_token)
        config.verify_token = dados.get('verify_token',config.verify_token)
        config.phone_number_id = dados.get('phone_number_id',config.phone_number_id)
        session.commit()
        return jsonify({"mensagem":"Configuracoes salvas com sucesso!"}), 200
    except Exception as e:
        session.rollback()
        return jsonify({"erro": str(e)}), 500
    finally:
        session.close()

@api_bp.route("/logs", methods = ['GET'])
def extrair_logs():
    if not os.path.exists(LOG_FILE):
        return jsonify([]), 200
    try:
        with open(LOG_FILE, 'r', encoding="utf-8") as f:
            logs = json.load(f)
        return jsonify(logs), 200
    except Exception as e:
        return jsonify({"erro": str(e)}),500

@api_bp.route('/clientes/<int:cliente_id>/lgpd-exportar', methods=['GET'])
def exportar_dados_cliente(cliente_id):
    session = get_session()
    try:
        cliente = session.query(Titular).filter(Titular.id == cliente_id).first()
        if not cliente:
            return jsonify({"erro":"Cliente nao encontrado!"}), 404
        mensagens = session.query(Mensagem).filter(Mensagem.titular_id == cliente_id).all()
        dados={
            "cliente":{
                "codcli":cliente.codcli,
                "nome": cliente.nome,
                "telefone": cliente.telefone,
                "notificacoes_ativas": cliente.notificacao_ativa
            },
            "mensagens":[{
                "tipo": m.tipo,
                "conteudo": m.conteudo,
                "data_envio": m.enviado_em.strftime("%d-%m-%Y %H:%M:%S") if m.enviado_em else None,
                "status": m.status
            }for m in mensagens]
        }
        memoria_file = io.BytesIO()
        memoria_file.write(json.dumps(dados, indent=4, ensure_ascii=False).encode('utf-8'))
        memoria_file.seek(0)
        return send_file(
            memoria_file,
            mimetype ="application/json",
            as_attachment=True,
            download_name=f"lgpd_export_{cliente.codcli}.json"
        )
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    finally:
        session.close()

@api_bp.route('/clientes/<int:cliente_id>/lgpd-excluir', methods=['DELETE'])
def excluir_dados_cliente(cliente_id):
    session = get_session()
    try:
        cliente = session.query(Titular).filter(Titular.id == cliente_id).first()
        if not cliente:
            return jsonify({"erro":"Cliente nao encontrado!"}), 404
        session.query(Mensagem).filter(Mensagem.titular_id == cliente_id).delete()
        cliente.telefone = "ANONIMIZADO"
        cliente.nome = "Cliente Anonimo (LGPD)"
        cliente.notificacao_ativa = False
        session.commit()
        registrar_log("LGPD_EXCLUSAO", "SUCESSO", {"cliente_id": cliente_id})
        return jsonify({"mensagem": "Dados do cliente apagados conforme regras da LGPD!"}), 200
    except Exception as e:
        session.rollback()
        return jsonify({"erro": str(e)}), 500
    finally:
        session.close()
VERIFY_TOKEN = os.getenv("TOKEN_AQUI", "boletoszap_verify_token")
@api_bp.route('/webhook', methods=['GET'])
def verificar_webhook():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    session = get_session()
    try:
        config = session.query(Configuracao).first()
        verify_token = (config.verify_token if config else None) or os.getenv('TOKEN_AQUI', 'boletoszap_verify_token')
        if mode == 'subscribe' and token == verify_token:
            print("Webhook verificado e ativo com sucesso!")
            return challenge, 200
        else:
            return jsonify({"erro":"Falha na verificacao do webhook"}), 403
    finally:
        session.close()
@api_bp.route("/webhook", methods =['POST'])
def receber_webhook():
    session = get_session()
    dados = request.get_json()
    try:
        if not dados or "entry" not in dados:
            return "ok",200
        for entry in dados['entry']:
            for change in entry.get("changes",[]):
                value = change.get('value',{})
                if 'statuses' in value:
                    for status_entry in value['statuses']:
                        meta_msg_id = status_entry.get("id")
                        novo_status = status_entry.get("status")
                        mensagem = session.query(Mensagem).filter(Mensagem.message_id == meta_msg_id).first()
                        if mensagem:
                            mensagem.status = novo_status
                            session.commit()
                            print(f"Status da mensagem de id {meta_msg_id} alterado para {novo_status}")
                elif 'messages' in value:
                    for message in value['messages']:
                        telefone_cliente = message.get("from")
                        texto_msg = message.get("text",{}).get("body","")
                        meta_msg_id = message.get('id')
                        titular = session.query(Titular).filter(Titular.telefone == telefone_cliente).first()
                        if titular:
                            nova_mensagem = Mensagem(
                                titular_id = titular.id,
                                boleto_id = 0,
                                tipo = 'recebida',
                                status = None,
                                conteudo = texto_msg,
                                enviado_em = datetime.now(),
                                message_id = meta_msg_id
                            )
                            session.add(nova_mensagem)
                            session.commit()
                            print(f"Nova mensagem recebida de {titular.nome}:{texto_msg}")
    except Exception as e:
        return jsonify({"erro":str(e)})
    finally:
        session.close()
    return "EVENT_RECEIVED",200

@api_bp.route("/boletos/<int:boleto_id>/enviar", methods=["POST"])
def enviar_manualmente(boleto_id):
    session = get_session()
    try:
        boleto = session.query(Boleto).filter(Boleto.id == boleto_id).first()
        if not boleto:
            return jsonify({"erro":"Boleto nao encontrado!"}),404
        titular = session.query(Titular).filter(Titular.id == boleto.titular_id).first()
        if not titular:
            return jsonify({"erro":"O cliente associadoa este boleto nao foi encontrado"}), 404
        config = session.query(Configuracao).first()
        if not config:
            config = Configuracao()
            session.add(config)
            session.commit()
        sucesso, retorno = enviar_mensagem(
            session,
            telefone=titular.telefone,
            nome=titular.nome,
            valor=boleto.valor,
            vencimento=boleto.data_vencimento,
            parcela_atual=boleto.parcela_atual,
            total_parcelas=boleto.total_parcelas,
            codigo_id=boleto.codigo_id,
            template_nome=config.template_nome
        )
        if sucesso:
            texto_mensagem = gerar_texto_template(
                config.template_nome,
                titular.nome,
                boleto.valor,
                boleto.data_vencimento,
                boleto.parcela_atual,
                boleto.total_parcelas,
                boleto.codigo_id
            )
            nova_mensagem = Mensagem(
                boleto_id=boleto.id,
                titular_id = titular.id,
                tipo = 'enviada',
                status = 'sent',
                conteudo = texto_mensagem,
                enviado_em = datetime.now(),
                message_id = retorno
            )
            session.add(nova_mensagem)
            session.commit()
            registrar_log(
                acao = 'ENVIO DE COBRANCA MANUAL',
                status = 'SUCESSO',
                detalhes = {
                    'cliente':titular.nome,
                    'telefone':titular.telefone,
                    'boleto_id':boleto.id,
                    'message_id':retorno
                }
            )
            return jsonify ({'mensagem':"Mensagem manual enviada com sucesso"}),200
        else:
            registrar_log(
                acao='ENVIO DE COBRANCA MANUAL',
                status='FALHA',
                detalhes={
                    'cliente':titular.nome,
                    'telefone':titular.telefone,
                    'boleto_id':boleto.id,
                    'erro':retorno
                }
            )
            return jsonify({'erro':retorno}),400
    except Exception as e:
        session.rollback()
        return jsonify({"erro":str(e)}),500
    finally:
        session.close()
