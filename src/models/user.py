from sqlalchemy import Boolean, Column, Integer, BigInteger, String, Enum
from models.base import Base
from enum import Enum as PyEnum


class UserRole(str, PyEnum):
    USER = "user"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, index=True)
    username = Column(String, nullable=True)
    agreement_accepted = Column(Boolean, default=False)
    referral_code = Column(String, nullable=True)

    role = Column(Enum(UserRole), nullable=False, default=UserRole.USER)

    banned = Column(Boolean, nullable=False, default=False)
