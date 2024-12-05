from fastapi import APIRouter
from database.session import DbSession

from services.user.params import *
from services.user.interactions import *

user_api_router = APIRouter(prefix="/user", tags=["User"])


@user_api_router.post("/create_user")
def create_user_api(db: DbSession, request: CreateUserRequest):  
    response = create_user(db, request.model_dump(exclude_none=True))
    return response


@user_api_router.post("/login_user")
def login_user_api(db: DbSession, request: LoginUserRequest): 
    response = login_user(db, request.model_dump(exclude_none=True))
    return response


@user_api_router.get("/list_users")
def list_users_api(db: DbSession):
    response = list_users(db)
    return response