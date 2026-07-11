from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from app.db.connection import Base

class Configuracao(Base):
    __tablename__ = "Configuracao"
    id = Column(Integer, primary_key=True, default=1)
    dias_antecedencia = Column(Integer, nullable=False, default=3)
    reenviar_apos_horas = Column(Integer, nullable=False, default=24)
    max_reenvios = Column(Integer, nullable=False, default=2)
    template_nome = Column(String(100), nullable=False, default="boleto_automatico_v1")
    horario_envio = Column(String(5), nullable=False, default="08:00")

