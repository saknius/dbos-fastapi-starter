import logging
from fastapi import status
from sqlalchemy import select
from fastapi.exceptions import HTTPException
from fastapi.encoders import jsonable_encoder

from services.cluster.models import Cluster
from services.deployment.models import Deployment
from services.deployment.params import CreateDeploymentRequest


class CreateDeployment:
    def __init__(self, db, request):
        self.db = db
        self.cluster = None
        self.deployment = None
        self.response = None
        self.request = CreateDeploymentRequest(**request)

    def get_cluster(self):
        self.cluster = self.db.scalars(
            select(Cluster)
            .where(
                Cluster.id == self.request.cluster_id,
                Cluster.status == "active",
            )
            .limit(1)
        ).first()

        if not self.cluster:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cluster Not Found!",
            )

    def validate_cluster_resources(self):
        if self.cluster.cpu_size < self.request.required_cpu:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cluster CPU is not enough!",
            )
        if self.cluster.ram_size < self.request.required_ram:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cluster RAM is not enough!",
            )
        if self.cluster.gpu_size < self.request.required_gpu:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cluster GPU is not enough!",
            )

    def create_deployment(self):
        self.deployment = Deployment(**self.request.model_dump(exclude_none=True))
        self.db.add(self.deployment)
        self.db.flush()

    def set_response(self):
        self.response = jsonable_encoder(self.deployment)

    def execute(self):
        self.get_cluster()
        self.validate_cluster_resources()
        self.create_deployment()
        self.set_response()
        return self.response


def create_deployment(db, request):
    return CreateDeployment(db, request).execute()
