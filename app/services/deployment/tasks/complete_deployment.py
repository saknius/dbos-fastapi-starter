import logging
from zoneinfo import ZoneInfo
from sqlalchemy import update, select
from datetime import datetime, timezone, timedelta

from services.cluster.models import Cluster
from services.deployment.models import Deployment
from services.deployment.enums import DeploymentEnums


class CompleteDeployment:
    """
    Handles marking deployments as completed and releasing cluster resources.
    """

    def __init__(self, db):
        self.db = db  # Database session
        self.completed_deployments = None  # List of deployments to be completed
        self.cluster_deployments = {}  # Tracks freed resources for clusters

    def get_completed_deployments(self):
        """
        Fetch deployments in the RUNNING state that have exceeded the execution time threshold.
        """
        self.completed_deployments = self.db.scalars(
            select(Deployment)
            .where(
                Deployment.state == DeploymentEnums.RUNNING.value,
                Deployment.updated_at
                < datetime.now(timezone.utc) - timedelta(seconds=10),
            )
            .order_by(Deployment.cluster_id)
        ).all()

    def calculate_cluster_free_resources(self):
        """
        Calculate resources to be freed for clusters based on completed deployments.
        """
        for deployment in self.completed_deployments:
            cluster_id = str(deployment.cluster_id)
            # Initialize cluster resource mapping if not present
            if cluster_id not in self.cluster_deployments:
                self.cluster_deployments[cluster_id] = {
                    "free_cpu": deployment.required_cpu,
                    "free_ram": deployment.required_ram,
                    "free_gpu": deployment.required_gpu,
                }
            else:
                # Add back resources used by the deployment
                self.cluster_deployments[cluster_id]["free_cpu"] += deployment.required_cpu
                self.cluster_deployments[cluster_id]["free_ram"] += deployment.required_ram
                self.cluster_deployments[cluster_id]["free_gpu"] += deployment.required_gpu

    def update_cluster_free_resources(self):
        """
        Update the available resources for clusters in the database.
        """
        for cluster_id, free_resources in self.cluster_deployments.items():
            cluster = self.db.scalar(select(Cluster).where(Cluster.id == cluster_id))
            # Add back freed resources to the cluster
            cluster.available_cpu += free_resources["free_cpu"]
            cluster.available_ram += free_resources["free_ram"]
            cluster.available_gpu += free_resources["free_gpu"]
            self.db.add(cluster)
            self.db.flush()

    def update_deployment_state(self):
        """
        Update the state of completed deployments to COMPLETED in the database.
        """
        if self.completed_deployments:
            completed_deployment_ids = [
                str(deployment.id) for deployment in self.completed_deployments
            ]
            self.db.execute(
                update(Deployment)
                .where(Deployment.id.in_(completed_deployment_ids))
                .values(
                    state=DeploymentEnums.COMPLETED.value,
                    updated_at=datetime.now(timezone.utc),
                )
            )

    def execute(self):
        """
        Execute the process of completing deployments and updating cluster resources.
        """
        self.get_completed_deployments()  # Step 1: Fetch completed deployments
        self.calculate_cluster_free_resources()  # Step 2: Calculate freed resources
        self.update_cluster_free_resources()  # Step 3: Update cluster resources
        self.update_deployment_state()  # Step 4: Mark deployments as completed
        return {
            "completed_deployments": [
                str(deployment.id) for deployment in self.completed_deployments
            ]
        }


def complete_deployment(db):
    """
    Wrapper function to execute the CompleteDeployment process.
    """
    return CompleteDeployment(db).execute()
