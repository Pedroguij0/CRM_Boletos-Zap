from datetime import date, timedelta, datetime
from sqlalchemy import select
from app.models import Boleto, Titular, Configuracao, Mensagem
from app.services.whatsapp import enviar_mensagem, gerar_texto_template
from app.services.lgpd import registrar_log

def processar_cobrancas(session):
    config = session.query(Configuracao).first()
    if not config:
        config = Configuracao()
        session.add(config)
        session.commit()
    hoje = date.today()
    data_alvo = hoje + timedelta(days=config.dias_antecedencia)
    vencimento_hoje = hoje
    atrasado_1_dia = hoje-timedelta(days=1)
    stmt= (
        select(Boleto).join(Titular)
        .where(Boleto.status.in_(["pendente", "atrasado"]))
        .where(Boleto.data_vencimento.in_([data_alvo, vencimento_hoje, atrasado_1_dia]))
        .where(Titular.notificacao_ativa == True)
    )
    boletos_cobrados = session.scalars(stmt).all()

    if not boletos_cobrados:
        registrar_log("ENVIO_AUTOMATICO", "SUCESSO", {"mensagem": "Nenhum boleto elegivel para cobranca hoje"})
        return 0
    enviados = 0
    for boleto in boletos_cobrados:
        titular = session.query(Titular).filter(Titular.id == boleto.titular_id).first()
        if not titular:
            continue
        sucessos, retorno = enviar_mensagem(
            session,
            telefone=titular.telefone,
            nome = titular.nome,
            valor= boleto.valor,
            vencimento = boleto.data_vencimento,
            parcela_atual= boleto.parcela_atual,
            total_parcelas= boleto.total_parcelas,
            codigo_id=  boleto.codigo_id,
            template_nome=config.template_nome
        )
        if sucessos:
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
                titular_id=titular.id,
                tipo="enviada",
                status="sent",
                conteudo=texto_mensagem,
                enviado_em=datetime.now(),
                message_id=retorno
            )
            session.add(nova_mensagem)
            enviados+=1
            registrar_log(
                acao='ENVIO COBRANCA',
                status = 'SUCESSO',
                detalhes ={
                    "cliente": titular.nome,
                    "telefone": titular.telefone,
                    "boleto_id":boleto.id,
                    "message_id":retorno

                }
            )
        else:
            registrar_log(
                acao='ENVIO_COBRANCA',
                status='FALHA',
                detalhes={
                    "cliente": titular.nome,
                    "telefone": titular.telefone,
                    "boleto_id": boleto.id,
                    "erro": retorno
                }
            )

    if enviados>0:
        session.commit()
    
    return enviados