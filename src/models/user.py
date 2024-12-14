from sqlalchemy import Boolean, Column, Integer, BigInteger, String
from models.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, index=True)
    username = Column(String, nullable=True)
    agreement_accepted = Column(Boolean, default=False)
    referral_code = Column(String, nullable=True)
