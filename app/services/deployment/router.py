from fastapi import APIRouter
from services.deployment.schemas.deployment_schemas import DeploymentCreate, DeploymentResponse
from services.deployment.interactions.create_deployment_api import create_deployment_api

deployment_router = APIRouter()

deployment_router.add_api_route(
    "/create_deployment",
    create_deployment_api,
    methods=["POST"],
    response_model=DeploymentResponse,
    summary="Create a new deployment"
)
