# app/utils/dependencies.py

from fastapi import Depends, HTTPException, status, Request
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from configs.config import settings
from services.user.params.user_params import TokenData
from services.user.models.user import User
from utils.security import ALGORITHM, oauth2_scheme

from libs.token.decode_token import decode_token


def get_db(request: Request):
    return request.state.db


async def get_current_user(request: Request):
    token = await oauth2_scheme(request)
    db: Session = request.state.db
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token({"bearer_token": token})
        if not payload.get("success"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Token!",
            )
    except JWTError as e:
        raise credentials_exception from e
    user = db.scalars(
        select(User)
        .where(User.id == payload.get("user_id"), User.status == "active")
        .limit(1)
    ).first()
    if user is None:
        raise credentials_exception
    return user
