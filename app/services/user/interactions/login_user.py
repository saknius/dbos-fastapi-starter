import bcrypt
import logging
from fastapi import status
from sqlalchemy import select
from datetime import datetime, timedelta
from fastapi.exceptions import HTTPException

from libs.token import encode_token
from services.user.models import User
from services.user.enums import UserStatus
from services.user.params import LoginUserRequest


class LoginUser:
    """
    Handles user authentication workflow: validating username and password,
    and generating a JWT token on successful login.
    """

    def __init__(self, db, request):
        self.db = db  # Database session
        self.user = None  # User object
        self.response = None  # Login response (JWT token)
        self.request = LoginUserRequest(**request)  # Validates and stores the request data

    def get_user(self):
        """
        Fetches the user from the database using the provided username.
        Ensures the user is active.
        """
        self.user = self.db.scalars(
            select(User)
            .where(
                User.username == self.request.username,
                User.status == UserStatus.ACTIVE.value,  # Ensure user is active
            )
            .limit(1)
        ).first()

        if not self.user:
            # Raise exception if user is not found or inactive
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect Username Or Password!",
            )

    def verify_password(self):
        """
        Verifies the password by comparing the input password with the stored hashed password.
        """
        binary_input_password = self.request.password.encode("utf-8")  # Convert input to bytes
        binary_stored_hashed_password = self.user.password.encode("utf-8")  # Convert stored hash to bytes
        verified = bcrypt.checkpw(binary_input_password, binary_stored_hashed_password)  # Compare passwords

        if not verified:
            # Raise exception if password verification fails
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect Username Or Password!",
            )

    def set_response(self):
        """
        Generates a JWT token for the authenticated user with a 1-day expiration.
        """
        self.response = encode_token({"user_id": self.user.id, "exp": datetime.now() + timedelta(days=1)})

    def execute(self):
        """
        Executes the login workflow:
        1. Fetch user from the database.
        2. Verify the provided password.
        3. Generate a JWT token on successful authentication.
        """
        self.get_user()
        self.verify_password()
        self.set_response()

        return self.response


def login_user(db, request):
    """
    Wrapper function to initialize and execute the LoginUser class.
    """
    return LoginUser(db, request).execute()
