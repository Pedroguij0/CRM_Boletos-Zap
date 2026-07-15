from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from app.db.connection import Base

class Configuracao(Base):
    __tablename__ = "Configuracao"
    id = Column(Integer, primary_key=True, default=1)
    dias_antecedencia = Column(Integer, nullable=False, default=3)
    template_nome = Column(String(100), nullable=False, default="boleto_automatico_v2")
    horario_envio = Column(String(5), nullable=False, default="09:00")
    meta_token = Column(String(500), nullable=True)
    phone_number_id = Column(String(100), nullable=True)
    verify_token = Column(String(100), nullable=True)

