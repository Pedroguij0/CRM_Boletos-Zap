from apscheduler.schedulers.background import BackgroundScheduler
from app.db import get_session
from app.services.cobranca import processar_cobrancas
from app.models import Configuracao
from datetime import datetime

scheduler = BackgroundScheduler()
def executar_cobrancas():
    print(f"{datetime.now()} - Iniciando a task diaria de verificacao de cobrancas...")
    session = get_session()
    try:
        enviados = processar_cobrancas(session)
        print(f"{datetime.now()} - Task finalizada. Quantidade de faturas enviadas: {enviados}")
    except Exception as e:
        print(f"{datetime.now()} - Erro ao executar a task: {e}")
    finally:
        session.close()

def iniciar_scheduler(app):
    ultima_execucao = {"dia":None}
    def verificar_e_executar():
        session =get_session()
        try:
            config = session.query(Configuracao).first()
            if not config:
                return
            horario_config = config.horario_envio or '09:00'
            agora = datetime.now()
            hoje = agora.date()
            hora_min = agora.strftime("%H:%M")
            if hora_min == horario_config and ultima_execucao["dia"] != hoje:
                ultima_execucao['dia'] = hoje
                executar_cobrancas()
        except Exception as e:
            print(f"Erro ao agendar a cobranca: {e}")
        finally:
            session.close()
    scheduler.add_job(verificar_e_executar, 'interval', minutes=1, id='cobrancas_diarias')
    scheduler.start()
    print("Agendador de cobrancas automaticas ativado em segundo plano!")