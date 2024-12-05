import re
import jwt
from uuid import UUID
from pydantic import BaseModel
from fastapi import status
from fastapi import HTTPException
from datetime import datetime, timezone
from fastapi.encoders import jsonable_encoder
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

from configs.config import settings


class EncodeTokenRequest(BaseModel):
    user_id: UUID
    exp: datetime


class EncodeTokenResponse(BaseModel):
    bearer_token: str


class EncodeToken:

    def __init__(self, request):
        self.response = None
        self.public_key = None
        self.private_key = None
        self.jwt_payload = None
        self.encoded_token = None
        self.request = EncodeTokenRequest(**request)
        self.set_keys()

    def set_keys(self):
        private_key_pem = settings.JWT_PRIVATE_KEY
        if not private_key_pem:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Private Key Not Found In Environment Variables!",
            )

        formatted_private_key = re.sub(r"\\n", "\n", private_key_pem)

        self.private_key = serialization.load_pem_private_key(formatted_private_key.encode(), password=None, backend=default_backend())

        self.public_key = self.private_key.public_key()

    def set_jwt_payload(self):
        self.jwt_payload = self.request.model_dump() | {
            "iat": int(datetime.now(timezone.utc).timestamp())
        }
        self.jwt_payload["exp"] = int(self.jwt_payload["exp"].timestamp())

    def encode_token(self):
        self.encoded_token = jwt.encode(
            jsonable_encoder(self.jwt_payload), self.private_key, algorithm="ES256"
        )

    def set_response(self):
        self.response = jsonable_encoder(
            EncodeTokenResponse(bearer_token=self.encoded_token)
        )

    def execute(self):
        self.set_jwt_payload()
        self.encode_token()
        self.set_response()

        return self.response


def encode_token(request):
    return EncodeToken(request=request).execute()
