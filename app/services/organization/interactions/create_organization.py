import uuid
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from services.organization.models.organization_user import OrganizationUser
from services.organization.models.organization import Organization
from services.organization.schemas.organization_schemas import CreateOrganizationRequest

class CreateOrganization:
    def __init__(self, db: Session, request: CreateOrganizationRequest):
        self.db = db
        self.request = CreateOrganizationRequest(**request)
        self.organization_id = None

    def execute(self):
        self.validate_organization_name()
        self.create_organization()
        if self.request.user_id:  
            self.create_organization_user()
        return {
            "id": str(self.organization_id),
        }

    def validate_organization_name(self):
        """
        Ensure the organization name is unique in the database.
        """
        if self.db.query(Organization).filter(Organization.name == self.request.name).first():
            raise HTTPException(status_code=400, detail="Organization name already exists.")

    def create_organization(self):
        """
        Create a new organization with a unique invite code.
        """
        invite_code = str(uuid.uuid4())[:8]  # Generate an 8-character unique invite code
        organization = Organization(name=self.request.name, invite_code=invite_code)
        self.db.add(organization)
        self.db.flush()
        self.organization_id = organization.id

    def create_organization_user(self):
        """
        Add the requesting user as a SuperAdmin of the newly created organization.
        """
        new_org_user = OrganizationUser(
            organization_id=self.organization_id,
            user_id=self.request.user_id,
            status="active",
        )
        self.db.add(new_org_user)
        self.db.flush()

def create_organization(db, request: CreateOrganizationRequest):
    """
    Entry point to create an organization and optionally associate a user with it.
    """
    return CreateOrganization(db=db, request=request).execute()
