from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ORM_table import User

engine = create_engine('sqlite:///Alice_db.sqlite')
session = sessionmaker(bind=engine)
s = session()


def check_user(request):
    if s.query(User).filter(User.id_user):
        pass
    else:
        user = User(id=request["session"]["user"]["user_id"], point_mem=0,
                    point_word=0)
        s.add(user)
        s.commit()


def add_point_mem(request):
    point = s.query(User).filter_by(
        id=request["session"]["user"]["user_id"]).one()
    if point:
        point.point_mem += 1
        s.add(point)
        s.commit()


def add_point_word(request):
    point = s.query(User).filter_by(
        id=request["session"]["user"]["user_id"]).one()
    if point:
        point.point_word += 1
        s.add(point)
        s.commit()
