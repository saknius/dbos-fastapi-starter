# app/services/organization/models/organization.py

from sqlalchemy import Column, String, UUID, ForeignKey
from sqlalchemy.types import  DateTime, Integer
from sqlalchemy.orm import relationship
import uuid
from constants.core_constants import CURRENT_TIMESTAMP
from database.session import Base

class OrganizationUser(Base):
    __tablename__ = "organization_users"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer,ForeignKey('organizations.id'), index=True, nullable=False)
    status = Column(String, default="active", index=True, nullable=False)
    user_id = Column(UUID, ForeignKey('users.id'), nullable=False)
    role_id = Column(Integer, nullable= True)
    created_at = Column(DateTime, nullable=False, default=CURRENT_TIMESTAMP)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=CURRENT_TIMESTAMP,
        onupdate=CURRENT_TIMESTAMP
    )

    users = relationship("User", backref="organization_users")
    organizations = relationship("Organization", backref="organization_users")

