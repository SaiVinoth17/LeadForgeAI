"""
SQLAlchemy ORM models for authentication tables.
Stored in the same SQLite DB as leads (data/leadforge.db).
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.orm import declarative_base

AuthBase = declarative_base()


class User(AuthBase):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    email = Column(String(320), unique=True, nullable=False, index=True)
    password_hash = Column(String(256), nullable=False, default="")
    role = Column(String(100), nullable=False, default="Agency Member")
    company = Column(String(200), nullable=False, default="My Agency")
    subscription = Column(String(100), nullable=False, default="Pro Tier")
    linked_providers = Column(Text, nullable=False, default="email")  # CSV
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "company": self.company,
            "subscription": self.subscription,
            "linked_providers": [p.strip() for p in self.linked_providers.split(",") if p.strip()],
        }


class PasswordResetToken(AuthBase):
    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    token = Column(String(256), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class RefreshTokenBlacklist(AuthBase):
    __tablename__ = "refresh_token_blacklist"

    id = Column(Integer, primary_key=True, autoincrement=True)
    jti = Column(String(256), unique=True, nullable=False, index=True)
    blacklisted_at = Column(DateTime, nullable=False, default=datetime.utcnow)
