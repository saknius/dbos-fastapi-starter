# app/services/authorization/models/policy_resource.py

from sqlalchemy import Column, Integer,ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database.session import Base

class PolicyResource(Base):
    __tablename__ = "policy_resources"
    policy_id = Column(Integer, ForeignKey('policies.id'), primary_key=True)
    resource_id = Column(Integer,ForeignKey('resources.id'), primary_key=True)

    policies = relationship('Policy', backref="policy_resources")



