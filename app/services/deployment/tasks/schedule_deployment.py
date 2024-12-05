from sqlalchemy import select, update, func
from fastapi.encoders import jsonable_encoder
from datetime import datetime, timezone
from services.deployment.enums import DeploymentEnums
from services.cluster.models import Cluster
from services.deployment.models import Deployment
from services.deployment.tasks.redis_lock import RedisLockManager

class ScheduleDeployment:
    """
    Handles the scheduling of deployments across clusters based on priority and resource availability.
    """

    def __init__(self, db, redis_db):
        self.db = db  # Database session
        self.redis_db = redis_db  # Redis connection for distributed locks
        self.page_size = 100  # Pagination size for cluster fetching
        self.triggered_deployments = []  # List of deployments that were triggered
        self.current_cluster_page = None
        self.queued_deployments = []  # Deployments waiting in the queue
        self.cluster_wise_mapping = {}  # Mapping of clusters to their queued deployments

    def sort_deployments_by_priority_and_resource_usage(self, deployments):
        """
        Sorts deployments first by priority (descending) and then by resource usage.
        """
        return sorted(
            deployments,
            key=lambda element: (
                -element["priority"],
                self.sort_by_resource_usage(element),
            ),
        )

    def sort_by_resource_usage(self, element):
        """
        Calculates the total resource usage for sorting purposes.
        """
        return (
            element["required_cpu"] + element["required_ram"] + element["required_gpu"]
        )

    def get_clusters(self):
        """
        Fetches a paginated list of clusters with a lock to prevent concurrent updates.
        """
        self.clusters = self.db.scalars(
            select(Cluster)
            .offset(self.current_cluster_page * self.page_size)
            .limit(self.page_size)
            .order_by(Cluster.id.asc())
            .with_for_update(skip_locked=True)
        ).all()

    def get_queued_deployments(self):
        """
        Fetches deployments in the QUEUED state for the retrieved clusters.
        """
        cluster_ids = [str(cluster.id) for cluster in self.clusters]
        self.queued_deployments = self.db.scalars(
            select(Deployment).where(
                Deployment.state == DeploymentEnums.QUEUED.value,
                Deployment.cluster_id.in_(cluster_ids),
            )
        ).all()

    def map_deployments_to_clusters(self):
        """
        Maps deployments to their respective clusters for efficient processing.
        """
        for queued_deployment in self.queued_deployments:
            if str(queued_deployment.cluster_id) not in self.cluster_wise_mapping:
                self.cluster_wise_mapping[str(queued_deployment.cluster_id)] = [
                    jsonable_encoder(queued_deployment)
                ]
            else:
                self.cluster_wise_mapping[str(queued_deployment.cluster_id)].append(
                    jsonable_encoder(queued_deployment)
                )

    def get_cluster_details(self):
        """
        Converts cluster details to a JSON-encoded format for easier resource updates.
        """
        self.clusters = {
            str(cluster.id): jsonable_encoder(cluster) for cluster in self.clusters
        }

    def check_if_deployment_can_be_scheduled(self, cluster_details, deployment):
        """
        Validates if the deployment can be scheduled on the given cluster.
        """
        return (
            deployment["required_cpu"] <= cluster_details["available_cpu"]
            and deployment["required_ram"] <= cluster_details["available_ram"]
            and deployment["required_gpu"] <= cluster_details["available_gpu"]
        )

    def update_cluster_details(self, cluster_id, deployment):
        """
        Deducts the resources of a deployment from the cluster's available resources.
        """
        self.clusters[cluster_id]["available_cpu"] -= deployment["required_cpu"]
        self.clusters[cluster_id]["available_ram"] -= deployment["required_ram"]
        self.clusters[cluster_id]["available_gpu"] -= deployment["required_gpu"]

    def update_deployment_state(self, deployment_id):
        """
        Updates the state of a deployment to RUNNING and appends it to the triggered list.
        """
        self.triggered_deployments.append(str(deployment_id))
        self.db.execute(
            update(Deployment)
            .where(Deployment.id == deployment_id)
            .values(
                state=DeploymentEnums.RUNNING.value,
                updated_at=datetime.now(timezone.utc),
            )
        )

    def update_cluster_remaining_resources(self, cluster_id):
        """
        Updates the cluster's available resources in the database.
        """
        cluster = self.clusters[cluster_id]
        self.db.execute(
            update(Cluster)
            .where(Cluster.id == cluster_id)
            .values(
                available_cpu=cluster["available_cpu"],
                available_ram=cluster["available_ram"],
                available_gpu=cluster["available_gpu"],
                updated_at=datetime.now(timezone.utc),
            )
        )

    def execute(self):
        """
        Orchestrates the entire scheduling process.
        """
        # Calculate total clusters and determine the current page
        cluster_count = int(self.db.scalar(select(func.count(Cluster.id))))
        self.current_cluster_page = RedisLockManager(self.redis_db).read_and_update(
            "current_cluster_page", self.page_size, cluster_count
        )

        # Retrieve and process clusters and deployments
        self.get_clusters()
        if self.clusters:
            self.get_queued_deployments()
            if self.queued_deployments:
                self.map_deployments_to_clusters()
                self.get_cluster_details()

                # Schedule deployments for each cluster
                for cluster_id, deployments in self.cluster_wise_mapping.items():
                    cluster_details = self.clusters[cluster_id]
                    deployments = self.sort_deployments_by_priority_and_resource_usage(
                        deployments
                    )
                    for deployment in deployments:
                        if self.check_if_deployment_can_be_scheduled(
                            cluster_details, deployment
                        ):
                            self.update_cluster_details(cluster_id, deployment)
                            self.update_deployment_state(deployment["id"])
                            self.update_cluster_remaining_resources(cluster_id)

        return {"triggered_deployments": self.triggered_deployments}


def schedule_deployment(db, redis_db):
    """
    Schedules deployments using the ScheduleDeployment class.
    """
    return ScheduleDeployment(db, redis_db).execute()
