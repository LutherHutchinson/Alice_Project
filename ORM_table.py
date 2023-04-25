from sqlalchemy import Column, Integer
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///Alice_db.sqlite')

Base = declarative_base()


class User(Base):
    __tablename__ = 'User'

    id_user = Column(Integer, primary_key=True)
    point_mem = Column(Integer)
    point_word = Column(Integer)


Base.metadata.create_all(engine)
