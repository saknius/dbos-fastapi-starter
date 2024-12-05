from services.user.models import User

def list_users(db):
    """
    Fetch all users from the database and return their details in a structured format.
    """
    users = db.query(User).all()
    return [
        {
            "id": user.id,
            "username": user.username,
            "display_name": user.display_name,
            "status": user.status,
            "created_at": user.created_at,
            "updated_at": user.updated_at
        }
        for user in users
    ]