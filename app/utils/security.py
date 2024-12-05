# app/utils/security.py

from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from configs.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "ES256"  # Use ES256 for ECDSA with P-256 curve

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, settings.JWT_PRIVATE_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# OAuth2 Password Bearer token URL
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login_user")
