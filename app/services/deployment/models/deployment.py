import uuid
from datetime import datetime, timezone, timedelta

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime

from database.session import Base

from constants.core_constants import CURRENT_TIMESTAMP

from services.deployment.enums import DeploymentEnums


class Deployment(Base):
    __tablename__ = "deployments"
    __table_args__ = {"extend_existing": True}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(), primary_key=True, server_default=func.gen_random_uuid()
    )
    cluster_id: Mapped[uuid.UUID] = mapped_column(
        UUID(), ForeignKey("clusters.id"), nullable=False
    )

    docker_image: Mapped[str] = mapped_column(String, nullable=False)
    required_cpu: Mapped[int] = mapped_column(Integer, nullable=False)
    required_ram: Mapped[float] = mapped_column(Float, nullable=False)
    required_gpu: Mapped[float] = mapped_column(Float, nullable=False)

    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    state: Mapped[str] = mapped_column(
        String, nullable=False, default=DeploymentEnums.QUEUED.value
    )

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

    clusters = relationship("Cluster", back_populates="deployments") 

