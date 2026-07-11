from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=False)
Session = sessionmaker(bind=engine)
Base = declarative_base()

def init_db():
    from app.models import titular, boleto, mensagem, config
    Base.metadata.create_all(engine)

def get_session():
    return Session()





