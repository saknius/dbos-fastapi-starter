from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from database.session import Base

class RolePolicy(Base):
    __tablename__ = "role_policies"

    role_id = Column(Integer, ForeignKey('roles.id'), primary_key=True)
    policy_id = Column(Integer,ForeignKey('policies.id'), primary_key=True)


