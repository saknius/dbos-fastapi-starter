from services.organization.models.organization import Organization

def list_organizations(db):
    organizations = db.query(Organization).all()
    return [
        {
            "id": org.id,
            "name": org.name,
            "invite_code": org.invite_code,
            "created_at": org.created_at,
            "updated_at": org.updated_at
        }
        for org in organizations
    ]