from fastapi import APIRouter
from database.session import DbSession
from services.organization.schemas.organization_schemas import CreateOrganizationRequest, JoinOrganizationRequest
from services.organization.interactions.create_organization import create_organization
from services.organization.interactions.join_organization import join_organization
from services.organization.interactions.list_organizations import list_organizations
from services.organization.interactions.list_organization_users import list_organization_users

organization_router = APIRouter(prefix='/organization', tags = ['organization'])

@organization_router.get("/list_organizations")
def list_organizations_api(db: DbSession):
    response = list_organizations(db)
    return response

@organization_router.get("/list_organization_users")
def list_organization_users_api(db: DbSession, organization_id: str):
    response = list_organization_users(db, organization_id)
    return response

@organization_router.post("/create_organization")
def create_organization_api(
    request: CreateOrganizationRequest,
    db: DbSession,
):
    response = create_organization(db, request.model_dump(exclude_none=True))
    return response

@organization_router.post("/join_organization")
def join_organization_api(
    request: JoinOrganizationRequest,
    db: DbSession,
):
    response = join_organization(db,  request.model_dump(exclude_none=True))
    return response

