from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    user_id = Column(String(255), nullable=False, unique=True)
    username = Column(String(255), default='unknown')
    firstname = Column(String(255), nullable=False)
    total_uses = Column(Integer, default=0)
    balance = Column(Integer, default=100)


class Referral(Base):
    __tablename__ = 'referrals'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    referrer_id = Column(Integer, ForeignKey('users.id'))


