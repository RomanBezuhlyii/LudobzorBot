from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_NAME = 'application.sqlite'

engine = create_engine('sqlite:///database/bot.db', echo=False)
Session = sessionmaker(bind=engine)

Base = declarative_base()

def create_database():
    Base.metadata.create_all(engine)