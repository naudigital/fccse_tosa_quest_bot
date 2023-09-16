import uuid

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    BigInteger,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class User(Base):
    """User model."""

    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    telegram_id = Column(BigInteger, nullable=False)
    first_name = Column(String, nullable=False)
    username = Column(String, nullable=True)


class Token(Base):
    """Token model."""

    __tablename__ = "tokens"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    name = Column(String, nullable=False)
    valid = Column(Boolean, default=True, nullable=False)


class Activation(Base):
    """Activation model."""

    __tablename__ = "activations"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        primary_key=True,
        nullable=False,
    )
    token_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tokens.id"),
        primary_key=True,
        nullable=False,
    )
    __table_args__ = (UniqueConstraint("user_id", "token_id"),)
    time = Column(DateTime(timezone=True), default=func.now(), nullable=False)
