# app/services/organization/models/organization.py

from sqlalchemy import Column, String
from sqlalchemy.types import DateTime, ARRAY, String, Integer
from sqlalchemy.orm import relationship
from constants.core_constants import CURRENT_TIMESTAMP
from database.session import Base

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    invite_code = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, nullable=False, default=CURRENT_TIMESTAMP)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=CURRENT_TIMESTAMP,
        onupdate=CURRENT_TIMESTAMP
    )

