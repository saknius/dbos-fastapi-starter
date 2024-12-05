from pydantic import BaseModel
from uuid import UUID

class CreateOrganizationRequest(BaseModel):
    name: str
    user_id: str | None = None

class JoinOrganizationRequest(BaseModel):
    invite_code: str
    user_id: str 

