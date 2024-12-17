from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    user_id = Column(String, nullable=False)
    username = Column(String(255), nullable=False)
    firstname = Column(String(255), nullable=True)
    available_uses = Column(Integer, default=0)
    total_uses = Column(Integer, default=0)
    balance = Column(Float, default=0.00)
    referrer_id = Column(Integer, ForeignKey('users.id'))
    referrer = relationship("User", remote_side=[id])


class Referral(Base):
    __tablename__ = 'referrals'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    referred_user_id = Column(Integer, ForeignKey('users.id'))


