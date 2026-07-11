from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.db.connection import Base

class Titular(Base):
    __tablename__ = "Titular"
    id = Column(Integer, primary_key= True, autoincrement= True)
    nome = Column(String(200), nullable = False)
    telefone = Column(String, nullable=False, unique=True)
    notificacao_ativa = Column(Boolean, default= True)
    ultimo_pagamento = Column(DateTime, default=func.now(), onupdate=func.now())
