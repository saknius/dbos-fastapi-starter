import bcrypt
import logging
from fastapi import status
from sqlalchemy import select
from fastapi.exceptions import HTTPException
from fastapi.encoders import jsonable_encoder

from configs.config import settings
from services.user.models import User
from services.user.enums import UserStatus
from services.user.params import CreateUserRequest

class CreateUser:
    """
    Handles the process of creating a new user, ensuring uniqueness,
    password security, and proper database insertion.
    """

    def __init__(self, db, request: CreateUserRequest):
        self.db = db  # Database session
        self.user = None  # User object to be created
        self.response = None  # Final response to return
        self.request = CreateUserRequest(**request)  # Validates and stores request data

    def check_username_uniqueness(self):
        """
        Checks if the username already exists in the database for active users.
        Raises an exception if a conflict is found.
        """
        existing_user = self.db.scalars(
            select(User)
            .where(
                User.username == self.request.username,
                User.status == UserStatus.ACTIVE.value,
            )
            .limit(1)
        ).first()

        if existing_user:
            # Raise exception if a user with the same username exists
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with the same username already exists!",
            )

    def encode_password(self):
        """
        Hashes the provided password using bcrypt and a predefined salt.
        The hashed password is stored in the request object.
        """
        binary_password = self.request.password.encode("utf-8")  # Convert password to bytes
        binary_salt = settings.PASSWORD_SALT.encode("utf-8")  # Convert salt to bytes
        binary_hashed_password = bcrypt.hashpw(binary_password, binary_salt)  # Hash password
        self.request.password = binary_hashed_password.decode("utf-8")  # Store hashed password as string

    def create_user(self):
        """
        Creates the user object and inserts it into the database.
        Commits the transaction after insertion.
        """
        self.user = User(
            username=self.request.username,
            display_name=self.request.display_name,
            password=self.request.password,
            status=UserStatus.ACTIVE.value,  # Mark user as active
        )
        self.db.add(self.user)
        self.db.commit()

    def set_response(self):
        """
        Prepares the final response, excluding the password for security.
        Adds a success message to the response.
        """
        self.response = jsonable_encoder(self.user) | {
            "message": "User created successfully!"
        }
        self.response.pop("password")  # Remove password from response for security

    def execute(self):
        """
        Executes the workflow:
        1. Check username uniqueness.
        2. Hash the password.
        3. Create the user in the database.
        4. Prepare the response.
        """
        self.check_username_uniqueness()
        self.encode_password()
        self.create_user()
        self.set_response()
        return self.response


def create_user(db, request):
    """
    Wrapper function to initialize and execute the CreateUser class.
    """
    return CreateUser(db, request).execute()
