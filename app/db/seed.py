from app.db import get_session
from app.models import Configuracao

def semear_banco():
    session = get_session()
    try:
        config_existente = session.query(Configuracao).first()
        if not config_existente:
            nova_config = Configuracao(
                dias_antecedencia=3,
                template_nome="boleto_automatico_v2",
                horario_envio="09:00",
                meta_token=None,
                phone_number_id=None,
                verify_token=None
            )
            session.add(nova_config)
            session.commit()
            print("Configuracao inicial semeada com sucesso!")
        else:
            print("Configuracao ja existente.")
    except Exception as e:
        session.rollback()
        print(f"Erro ao semear o banco de dados: {e}")
    finally:
        session.close()

if __name__ == '__main__':
    semear_banco()