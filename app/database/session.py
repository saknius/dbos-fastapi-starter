from typing import Annotated
from fastapi import Depends, Request
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine, event, inspect
from sqlalchemy.ext.declarative import declarative_base

from configs.config import settings

# Create a database engine
# This establishes the connection to the database using the URL provided in the environment variables.
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency for retrieving a database session
def get_db(request: Request):
    return request.state.db

# Type alias for database session dependency
# This provides a type-annotated way to include the database session in route handlers.
DbSession = Annotated[Session, Depends(get_db)]
