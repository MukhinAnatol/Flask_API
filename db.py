import atexit
from sqlalchemy import Column, String, Integer, DateTime, create_engine, func, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from server import HttpError

PG_DSN = 'postgresql://app:1234@127.0.0.1:5431/testdb'

engine = create_engine(PG_DSN)
Base = declarative_base()
Session = sessionmaker(bind=engine)

atexit.register(engine.dispose)

class User(Base):

    __tablename__ = 'ads_users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False, unique=True, index=True)
    password = Column(String, nullable=False)
    registration_time = Column(DateTime, server_default=func.now())

def get_user(session: Session, user_id: int):
    user = session.query.get(user_id)
    if user is None:
        raise HttpError(404, 'user not found')
    return user


class Adv(Base):

    __tablename__ = "advertisement"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False, index=True)
    description = Column(String, nullable=False)
    creation_time = Column(DateTime, server_default=func.now())
    user_id = Column(Integer, ForeignKey("ads_users.id"), ondelete="CASCADE")
    user = relationship("User", lazy="joined")

def get_adv(session: Session, adv_id: int):
    adv = session.query(Adv).get(adv_id)
    if adv is None:
        raise HttpError(404, 'advertisement not found')
    return adv

Base.metadata.create.all(bind=engine)