
from fastapi import APIRouter
from services.cluster.schemas.cluster_schemas import ClusterCreate, ClusterResponse
from services.cluster.interactions.create_cluster_api import create_cluster_api

cluster_router = APIRouter()

cluster_router.add_api_route(
    "/create_cluster",
    create_cluster_api,
    methods=["POST"],
    response_model=ClusterResponse,
    summary="Create a new cluster"
)
