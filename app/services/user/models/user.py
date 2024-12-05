import uuid
from datetime import datetime, timezone, timedelta

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime

from database.session import Base
from constants.core_constants import CURRENT_TIMESTAMP


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"extend_existing": True}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(), primary_key=True, server_default=func.gen_random_uuid()
    )
    username: Mapped[str] = mapped_column(String, nullable=False)

    display_name: Mapped[str] = mapped_column(String, nullable=False)

    password: Mapped[str] = mapped_column(String, nullable=False)


    status: Mapped[str] = mapped_column(String, nullable=False, default="active")

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=CURRENT_TIMESTAMP
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=CURRENT_TIMESTAMP,
        onupdate=CURRENT_TIMESTAMP,
    )
