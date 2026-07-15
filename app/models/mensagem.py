from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Date, ForeignKey
from app.db.connection import Base

class Mensagem(Base):
    __tablename__ = "Mensagem"
    id = Column(Integer, primary_key=True, autoincrement=True)
    boleto_id = Column(Integer, ForeignKey("Boleto.id"), nullable=False)
    titular_id = Column(Integer, ForeignKey("Titular.id"), nullable=False)
    conteudo = Column(Text, nullable=False)
    enviado_em = Column(DateTime, nullable=False)
    status = Column(String(20), nullable=True)
    tipo= Column(String(20), nullable=False)
    message_id = Column(String(200), nullable=True)

    

