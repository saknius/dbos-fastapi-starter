from services.organization.models.organization_user import OrganizationUser
from services.user.models import User

def list_organization_users(db, organization_id):
    """
    Fetch all users associated with a specific organization.

    Args:
        db: Database session.
        organization_id: The ID of the organization to fetch users for.

    Returns:
        A list of dictionaries containing user and organization-user details.
    """
    # Query organization-user mappings for the specified organization
    organization_users = db.query(OrganizationUser).filter(
        OrganizationUser.organization_id == organization_id
    ).all()

    # Format the response with user and mapping details
    return [
        {
            "id": org_user.id,
            "organization_id": org_user.organization_id,
            "user_id": org_user.user_id,
            "user_details": {
                "username": user.username,
                "display_name": user.display_name,
                "status": user.status,
            } if (user := db.query(User).filter(User.id == org_user.user_id).first()) else None,
            "status": org_user.status,
            "created_at": org_user.created_at,
            "updated_at": org_user.updated_at,
        }
        for org_user in organization_users
    ]
