from datetime import date, timedelta
from sqlalchemy import select
from app.models import Boleto

def atualizar_status_boleto(session):
    hoje = date.today()
    stmt = select(Boleto).where(Boleto.status != "pago")
    boletos = session.scalars(stmt).all()
    modificados = 0
    for boleto in boletos:
        novo_status = "atrasado" if boleto.data_vencimento < hoje else "pendente"
        if boleto.status != novo_status:
            boleto.status = novo_status
            modificados += 1
    if modificados >0:
        session.commit()
    return modificados

def registrar_pagamento(session, boleto_id, data_pagamento=None):
    stmt = select(Boleto).where(Boleto.id == boleto_id)
    boleto = session.scalar(stmt)
    if not boleto:
        return False, "Boleto não encontrado."
    
    hoje = date.today()
    if data_pagamento and data_pagamento > hoje:
        return False, "A data de pagamento deve ser anterior ou igual a data atual"
    
    boleto.status = "pago"
    boleto.data_pagamento = data_pagamento or hoje
    if boleto.parcela_atual < boleto.total_parcelas:
        proximo_vencimento = boleto.data_vencimento + timedelta(days=30)
        novo_boleto = Boleto(
            titular_id=boleto.titular_id,
            codigo_id=f"{boleto.codigo_id}-P{boleto.parcela_atual+1}",
            parcela_atual=boleto.parcela_atual + 1,
            total_parcelas=boleto.total_parcelas,
            valor=boleto.valor,
            data_vencimento=proximo_vencimento,
            status="pendente"
        )
        session.add(novo_boleto)
    session.commit()
    return True, "Pagamento liquidado com sucesso!"

