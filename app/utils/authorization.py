# app/utils/authorization.py

from sqlalchemy.orm import Session
from database.session import DbSession
from services.authorization.models.role_policy import RolePolicy
from services.authorization.models.policy_resource import PolicyResource
from services.authorization.models.resource import Resource

def get_user_permissions(role_id, request):
    db: Session = request.state.db
    # Get all policy IDs associated with the role
    policy_ids = db.query(RolePolicy.policy_id).filter(RolePolicy.role_id == role_id).distinct().subquery()
    # Get all resource IDs associated with the policies
    resource_ids = db.query(PolicyResource.resource_id).filter(PolicyResource.policy_id.in_(policy_ids)).subquery()
    # Get all resources
    resources = db.query(Resource).filter(Resource.id.in_(resource_ids)).all()
    return resources
  
