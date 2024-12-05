import logging
from fastapi import APIRouter
from database.session import DbSession


from services.cluster.params import *
from services.cluster.interactions import *


cluster_api_router = APIRouter(prefix="/cluster", tags=["Clusters"])


@cluster_api_router.post("/create_cluster")
def create_cluster_api(db: DbSession, request: CreateClusterRequest):
    response = create_cluster(db, request.model_dump(exclude_none=True))
    return response


@cluster_api_router.put("/update_cluster")
def update_cluster_api(db: DbSession, request: UpdateClusterRequest):
    response = update_cluster(db, request.model_dump(exclude_none=True))
    return response
