import pandas as pd
from app.models import Titular, Boleto

def tratamento_telefone(tel):
    if pd.isna(tel):
        return None
    numero_tel = "".join(filter(str.isdigit, str(tel)))
    if not numero_tel:
        return None
    if not numero_tel.startswith("55"):
        numero_tel= "55" + numero_tel
    return numero_tel

def importar_clientes(session, caminho_excel):
    df = pd.read_excel(caminho_excel)
    cadastrados = 0
    for _, linha in df.iterrows():
        if pd.isna(linha.get('CODCLI')) or pd.isna(linha.get('CLIENTE')):
            continue
        codcli = int(linha["CODCLI"])
        nome = str(linha["CLIENTE"]).strip()
        telefone_cru = None
        for coluna in ['TELCOB', 'TELCOM', 'TELENT', 'TELEFONE']:
            if coluna in linha and not pd.isna(linha[coluna]) and str(linha[coluna]).strip() != "":
                telefone_cru = linha[coluna]
                break
        telefone_tratado = tratamento_telefone(telefone_cru)
        if not telefone_tratado:
            continue
        existente = session.query(Titular).filter(
            (Titular.codcli == codcli) | (Titular.telefone == telefone_tratado)
        ).first()
        if not existente:
            novo_titular = Titular(
                codcli = codcli,
                nome = nome,
                telefone = telefone_tratado,
                notificacao_ativa = True
            )
            session.add(novo_titular)
            cadastrados+=1
    session.commit()
    return cadastrados

def importar_boletos(session, caminho_excel):
    df = pd.read_excel(caminho_excel)
    cadastrados = 0
    for _, linha in df.iterrows():
        if pd.isna(linha.get('CODCLI')) or pd.isna(linha.get('LINHADIG')):
            continue
        codcli = int(linha['CODCLI'])
        valor = float(linha['VALOR'])
        prestacao = int(linha['PREST'])
        data_vencimento = pd.to_datetime(linha['DTVENC']).date()
        linha_digitavel = str(linha['LINHADIG']).strip()
        titular = session.query(Titular).filter(Titular.codcli == codcli).first()
        if not titular:
            continue
        existente = session.query(Boleto).filter(Boleto.codigo_id == linha_digitavel).first()
        if not existente:
            novo_boleto = Boleto(
                titular_id = titular.id,
                codigo_id = linha_digitavel,
                valor = valor,
                data_vencimento=data_vencimento,
                parcela_atual=prestacao,
                total_parcelas=prestacao,
                status = "pendente"
            )
            session.add(novo_boleto)
            cadastrados+=1
    session.commit()
    return cadastrados

    