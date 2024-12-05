import logging
from fastapi import APIRouter
from database.session import DbSession
from database.redis_db import redis_db

from services.deployment.params import *
from services.deployment.interactions import *
from services.deployment.tasks.schedule_deployment import schedule_deployment
from services.deployment.tasks.complete_deployment import complete_deployment

deployment_api_router = APIRouter(prefix="/deployment", tags=["Deployments"])


@deployment_api_router.post("/create_deployment")
def create_deployment_api(db: DbSession, request: CreateDeploymentRequest):
    response = create_deployment(db, request.model_dump(exclude_none=True))
    return response


@deployment_api_router.post("/schedule_deployment")
def schedule_deployment_api(db: DbSession):
    response = schedule_deployment(db, redis_db)
    return response


@deployment_api_router.post("/complete_deployment")
def complete_deployment_api(db: DbSession):
    response = complete_deployment(db)
    return response
