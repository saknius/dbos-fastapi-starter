import logging
from fastapi import status
from sqlalchemy import select
from fastapi.exceptions import HTTPException
from fastapi.encoders import jsonable_encoder

from services.deployment.enums import DeploymentState
from services.deployment.models.deployment import Deployment
from services.cluster.models.cluster import Cluster
from services.cluster.params import UpdateClusterRequest


class UpdateCluster:

    def __init__(self, db, request):
        self.db = db
        self.cluster = None
        self.deployments = []
        self.request = UpdateClusterRequest(**request)

    def get_cluster(self):
        self.cluster = self.db.scalars(
            select(Cluster)
            .where(Cluster.id == self.request.id, Cluster.status == "active")
            .limit(1)
        ).first()

        if not self.cluster:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cluster Not Found",
            )

    def get_deployments(self):
        self.deployments = self.db.scalars(
            select(Deployment).where(
                Deployment.cluster_id == self.request.id,
                Deployment.state.in_(
                    [DeploymentState.RUNNING.value, DeploymentState.QUEUED.value]
                ),
                Deployment.status == "active",
            )
        ).all()

    def check_resource_limits(self):
        max_cpu = max([deployment.required_cpu for deployment in self.deployments])
        max_ram = max([deployment.required_ram for deployment in self.deployments])
        max_gpu = max([deployment.required_gpu for deployment in self.deployments])

        if self.request.cpu_size:
            if self.request.cpu_size < max_cpu:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot Update Cluster CPU Size As A Currently Running Deployment Requires More CPU",
                )
            self.cluster.cpu_size = self.request.cpu_size

        if self.request.ram_size:
            if self.request.ram_size < max_ram:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot Update Cluster RAM Size As A Currently Running Deployment Requires More RAM",
                )
            self.cluster.ram_size = self.request.ram_size

        if self.request.gpu_size:
            if self.request.gpu_size < max_gpu:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot Update Cluster GPU Size As A Currently Running Deployment Requires More GPU",
                )
            self.cluster.gpu_size = self.request.gpu_size

    def check_name_uniqueness(self):
        if self.request.name:
            existing_cluster = self.db.scalars(
                select(Cluster).where(
                    Cluster.id != self.request.id,
                    Cluster.status == "active",
                    Cluster.name == self.request.name,
                )
            ).first()
            if existing_cluster:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cluster Name Must Be Unique",
                )
            self.cluster.name = self.request.name

    def check_cluster_deletion(self):
        if self.request.delete:
            if self.deployments:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot Delete Cluster With Running Deployments",
                )

    def check_cluster_status(self):
        if self.request.status:
            if self.request.status == "inactive":
                if self.deployments:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Cannot Update Cluster Status While Deployments Are Running",
                    )
                else:
                    self.cluster.status = self.request.status

    def set_response(self):
        self.db.add(self.cluster)
        self.db.flush()
        return jsonable_encoder(self.cluster)

    def execute(self):
        self.get_cluster()
        self.get_deployments()
        self.check_name_uniqueness()
        self.check_resource_limits()
        self.check_cluster_status()
        return self.set_response()


def update_cluster(db, request):
    return UpdateCluster(db, request).execute()
