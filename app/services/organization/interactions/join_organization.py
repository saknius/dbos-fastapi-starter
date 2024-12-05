from fastapi import  HTTPException
from sqlalchemy.orm import Session

from services.organization.models.organization import Organization
from services.organization.models.organization_user import OrganizationUser
from services.organization.schemas.organization_schemas import JoinOrganizationRequest

class JoinOrganization:
    """
    Handles the process of adding a user to an organization using an invite code.
    Ensures validations and database updates are performed correctly.
    """

    def __init__(self, db: Session, request: JoinOrganizationRequest):
        self.db = db  # Database session
        self.request = JoinOrganizationRequest(**request)  # Validates and stores the request data

    def execute(self):
        """
        Main workflow to validate the invite code and add the user to the organization.
        Returns a success message upon completion.
        """
        self.perform_validations()  # Ensure all validations are passed
        self.add_user_to_organization()  # Add the user to the organization
        return {
            'message': 'User added to organization'
        }

    def perform_validations(self):
        """
        Performs all necessary validations before adding a user to the organization.
        """
        self.validate_invite_code()  # Validate the invite code
        self.validate_user_membership()  # Ensure the user is not already a member

    def validate_invite_code(self):
        """
        Checks if the invite code is valid and retrieves the associated organization.
        Raises an exception if the code is invalid.
        """
        organization = self.db.query(Organization).filter(Organization.invite_code == self.request.invite_code).first()
        if not organization:
            raise HTTPException(status_code=400, detail="Invalid invite code.")
        self.organization = organization  # Store the organization for further use

    def validate_user_membership(self):
        """
        Checks if the user is already a member of the organization.
        Raises an exception if the user is already a member.
        """
        membership = self.db.query(OrganizationUser).filter(
            OrganizationUser.user_id == self.request.user_id,
            OrganizationUser.organization_id == self.organization.id
        ).first()
        
        if membership:
            raise HTTPException(status_code=400, detail="User is already a member of this organization.")

    def add_user_to_organization(self):
        """
        Creates a new membership record for the user in the organization.
        Adds the record to the database.
        """
        new_membership = OrganizationUser(user_id=self.request.user_id, organization_id=self.organization.id)
        self.db.add(new_membership)
        self.db.flush()  # Commit the new membership record


def join_organization(db, request):
    """
    Wrapper function to initialize and execute the JoinOrganization workflow.
    """
    return JoinOrganization(db, request).execute()
