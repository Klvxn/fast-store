from sqlalchemy import Column, Integer, String, Boolean, DateTime, func

from config.database import FastModel


class User(FastModel):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)

    email = Column(String, nullable=False)
    username = Column(String(25))

    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    password = Column(String, nullable=False)
    totp_secret = Column(String)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, nullable=True, onupdate=func.now())
