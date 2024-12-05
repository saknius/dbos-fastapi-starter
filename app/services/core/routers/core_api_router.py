import logging
from fastapi import APIRouter

from services.core.interactions import *

core_api_router = APIRouter(prefix="/core", tags=["Core"])


@core_api_router.get("/health")
def health_check():
    
    return {
        "status": "ok",
        "success": True,
        "version": "0.0.1",
        "message": "Hello From MLOps Platform!",
    }


@core_api_router.get("/create_tables")
def create_tables_api():
    response = create_tables()
    return response

@core_api_router.get("/drop_tables")
def drop_tables_api():
    response = drop_tables()
    return response

