from database.session import Base, engine
from fastapi import APIRouter, HTTPException
from database.session import Base, engine
from services.user.models import *
from services.cluster.models import *
from services.deployment.models import *
from services.organization.models.organization import Organization
from services.organization.models.organization_user import OrganizationUser
from services.authorization.models.role import Role
from services.authorization.models.policy import Policy
from services.authorization.models.role_policy import RolePolicy
from services.authorization.models.role import Role
from services.authorization.models.resource import Resource
from services.authorization.models.policy_resource import PolicyResource

router = APIRouter()

class DropTables:
    def __init__(self):
        pass

    def execute(self):
        try:
            Base.metadata.drop_all(bind=engine)
            return {"message": "Tables Dropped Successfully!"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error while dropping tables: {str(e)}")


def drop_tables():
    return DropTables().execute()