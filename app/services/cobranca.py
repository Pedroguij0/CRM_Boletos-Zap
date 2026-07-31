from datetime import date, timedelta, datetime
from sqlalchemy import select
from app.models import Boleto, Titular, Configuracao, Mensagem
from app.services.whatsapp import enviar_mensagem, gerar_texto_template
from app.services.lgpd import registrar_log
from app.services.boleto_service import atualizar_status_boleto

def processar_cobrancas(session):
    # Atualiza automaticamente o status dos boletos vencidos para 'atrasado'
    atualizar_status_boleto(session)

    config = session.query(Configuracao).first()
    if not config:
        config = Configuracao()
        session.add(config)
        session.commit()
    hoje = date.today()
    datas_antecedentes = [hoje + timedelta(days=d) for d in range(1,(config.dias_antecedencia or 0)+1)]
    vencimento_hoje = hoje
    data_hoje = [hoje]
    datas_subsequentes = [hoje - timedelta(days=d) for d in range(1,(config.dias_subsequencia or 0)+1)]
    datas_elegiveis = datas_antecedentes + data_hoje + datas_subsequentes
    stmt= (
        select(Boleto).join(Titular)
        .where(Boleto.status.in_(["pendente", "atrasado"]))
        .where(Boleto.data_vencimento.in_(datas_elegiveis))
        .where(Titular.notificacao_ativa == True)
    )
    boletos_a_cobrar = session.scalars(stmt).all()

    if not boletos_a_cobrar:
        registrar_log("ENVIO_AUTOMATICO", "SUCESSO", {"mensagem": "Nenhum boleto elegivel para cobranca hoje"})
        return 0
    enviados = 0
    enviado_hoje = datetime.combine(hoje, datetime.min.time())
    for boleto in boletos_a_cobrar:
        titular = session.query(Titular).filter(Titular.id == boleto.titular_id).first()
        if not titular:
            continue
        boleto_enviado_hoje = session.query(Mensagem).filter(
            Mensagem.boleto_id == boleto.id,
            Mensagem.enviado_em >= enviado_hoje
        ).first()
        if boleto_enviado_hoje:
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
                status='SUCESSO',
                detalhes={
                    "Boleto": boleto.codigo_id,
                    "Cliente": titular.nome,
                    "Telefone": titular.telefone,
                    "Conteúdo da Mensagem": texto_mensagem
                }
            )
        else:
            registrar_log(
                acao='ENVIO COBRANCA',
                status='FALHA',
                detalhes={
                    "Boleto": boleto.codigo_id,
                    "Cliente": titular.nome,
                    "Telefone": titular.telefone,
                    "Erro": retorno
                }
            )

    if enviados>0:
        session.commit()
    
    return enviados