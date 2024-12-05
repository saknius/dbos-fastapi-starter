import re
import jwt
import logging
from uuid import UUID
from fastapi import status
from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

from configs.config import settings


class DecodeTokenRequest(BaseModel):
    bearer_token: str


class DecodeTokenResponse(BaseModel):
    success: bool
    user_id: Optional[UUID] = None
    iat: Optional[datetime] = None
    exp: Optional[datetime] = None


class DecodeToken:

    def __init__(self, request):
        self.response = None
        self.public_key = None
        self.request = request
        self.private_key = None
        self.decoded_token = None
        self.set_keys()

    def set_keys(self):
        private_key_pem = settings.JWT_PRIVATE_KEY
        if not private_key_pem:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Private Key Not Found In Environment Variables!",
            )

        formatted_private_key = re.sub(r"\\n", "\n", private_key_pem)

        self.private_key = serialization.load_pem_private_key(
            formatted_private_key.encode(), password=None, backend=default_backend()
        )

        self.public_key = self.private_key.public_key()

    def set_request(self):
        self.request = DecodeTokenRequest(**self.request)

    def decode_token(self):
        try:
            self.decoded_token = jwt.decode(
                self.request.bearer_token, self.public_key, algorithms=["ES256"]
            )
        except Exception as e:
            pass
            logging.warning(
                "Token Decode Error -> {error_message}".format(error_message=str(e))
            )

    def set_response(self):
        if self.decoded_token:
            self.response = DecodeTokenResponse(
                **(self.decoded_token | {"success": True})
            )
        else:
            self.response = DecodeTokenResponse(**{"success": False})

    def set_error_response(self):
        self.response = DecodeTokenResponse(**{"success": False})

    def json_encode_response(self):
        self.response = jsonable_encoder(self.response)

    def execute(self):

        try:
            self.set_request()
            self.decode_token()
            self.set_response()

        except Exception as e:
            self.set_error_response()

        self.json_encode_response()
        return self.response


def decode_token(request):
    return DecodeToken(request=request).execute()
