import re
from fastapi import status
from typing import Optional
# from pydantic import BaseModel, model_validator
from fastapi.exceptions import HTTPException


class CreateUserRequest(BaseModel):
    username: str
    display_name: Optional[str] = None
    password: str

    # @model_validator(mode="before")
    def populate_display_name(cls, values):
        display_name = values.get("display_name")
        if not display_name:
            values["display_name"] = values["username"]
        return values

    # @model_validator(mode="before")
    def validate_password(cls, values):
        password = values.get("password")
        if not password:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Password is required",
            )
        if len(password) < 8:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Password must be at least 8 characters long",
            )
    
        if not re.search(r"[A-Z]", password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must contain at least one uppercase letter",
            )

        if not re.search(r"[a-z]", password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must contain at least one lowercase letter",
            )

        if not re.search(r"\d", password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must contain at least one numeric digit",
            )

        if not re.search(r"[@$!%*?&]", password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must contain at least one special character (@, $, !, %, *, ?, &, -, _)",
            )
        return values


class LoginUserRequest(BaseModel):
    username: str
    password: str


class TokenData(BaseModel):
    username: Optional[str] = None