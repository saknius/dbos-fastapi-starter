import uuid
from datetime import datetime, timezone, timedelta

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime
from constants.core_constants import CURRENT_TIMESTAMP
from database.session import Base
from constants.core_constants import CURRENT_TIMESTAMP

class Cluster(Base):
    __tablename__ = "clusters"
    __table_args__ = {"extend_existing": True}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(), primary_key=True, server_default=func.gen_random_uuid()
    )
    organization_id = Column(Integer,ForeignKey('organizations.id'), nullable=False)

    name: Mapped[str] = mapped_column(String, nullable=False)

    cpu_size: Mapped[int] = mapped_column(Integer, nullable=False)
    available_cpu: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    ram_size: Mapped[float] = mapped_column(Float, nullable=False)
    available_ram: Mapped[float] = mapped_column(Float, nullable=False, default=0)

    gpu_size: Mapped[float] = mapped_column(Float, nullable=False)
    available_gpu: Mapped[float] = mapped_column(Float, nullable=False, default=0)

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

    organization = relationship("Organization", backref="clusters")
    deployments = relationship("Deployment", back_populates="clusters")
