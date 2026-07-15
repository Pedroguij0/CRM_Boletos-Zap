from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, CheckConstraint
from datetime import date
from app.db.connection import Base

class Boleto(Base):
    __tablename__ = "Boleto"
    id= Column(Integer, primary_key=True, autoincrement=True)
    titular_id = Column(Integer, ForeignKey("Titular.id"), nullable=False)
    codigo_id = Column(String(50), nullable=False, unique=True)
    parcela_atual = Column(Integer, nullable=False)
    total_parcelas = Column(Integer, nullable=False)
    criado_em = Column(Date, nullable=False, default=date.today)
    valor = Column(Float, nullable=False)
    data_vencimento = Column(Date, nullable=False)
    data_pagamento = Column(Date, nullable=True)
    status = Column(String(20), default="pendente")
    __table_args__ = (
    CheckConstraint(status.in_(["pendente", "pago", "atrasado"]), name="status_valido"),)

