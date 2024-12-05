import logging
from sqlalchemy import select
from fastapi.exceptions import HTTPException
from fastapi.encoders import jsonable_encoder
from services.organization.models.organization_user import OrganizationUser
from services.cluster.models import Cluster
from services.cluster.params import CreateClusterRequest


class CreateCluster:
    """
    Handles the creation of a new cluster in an organization.
    """

    def __init__(self, db, request):
        self.db = db  # Database session
        self.cluster = None  # Cluster object to be created
        self.request = CreateClusterRequest(**request)  # Validates and stores the request data

    def check_creation_permission(self):
        """
        Verifies if the user has permission to create a cluster in the organization.
        """
        user_belongs_to_organization = self.db.scalars(
            select(OrganizationUser)
            .where(
                OrganizationUser.user_id == self.request.user_id,
                OrganizationUser.organization_id == self.request.organization_id,
                OrganizationUser.status == "active",  # Ensure the user is active in the organization
            )
            .limit(1)
        ).first()
        if not user_belongs_to_organization:
            raise HTTPException(
                status_code=403,
                detail="You Don't Have Permission To Create A Cluster For This Organization!",
            )

    def check_cluster_name_uniqueness(self):
        """
        Ensures that the cluster name is unique within active clusters.
        """
        cluster_with_same_name = self.db.scalars(
            select(Cluster)
            .where(
                Cluster.name == self.request.name,
                Cluster.status == "active",  # Check for active clusters
            )
            .limit(1)
        ).first()

        if cluster_with_same_name:
            raise HTTPException(
                status_code=400,
                detail="A Cluster With Same Name Already Exists!",
            )

    def create_cluster(self):
        """
        Creates the cluster with initial resources (CPU, RAM, GPU).
        """
        cluster = self.request.model_dump(exclude={"user_id"})  # Exclude user_id from creation
        cluster["available_cpu"] = cluster["cpu_size"]  # Initialize available resources
        cluster["available_ram"] = cluster["ram_size"]
        cluster["available_gpu"] = cluster["gpu_size"]
        self.cluster = Cluster(**cluster)  # Create the cluster object
        self.db.add(self.cluster)  # Add to the database session
        self.db.flush()  # Flush changes to generate IDs

    def set_response(self):
        """
        Prepares the response by serializing the created cluster object.
        """
        self.response = jsonable_encoder(self.cluster)

    def execute(self):
        """
        Executes the cluster creation workflow in the following steps:
        1. Check name uniqueness.
        2. Create the cluster with specified resources.
        3. Prepare the response for the created cluster.
        """
        self.check_cluster_name_uniqueness()
        self.create_cluster()
        self.set_response()
        return self.response


def create_cluster(db, request):
    """
    Wrapper function to initialize and execute the CreateCluster class.
    """
    return CreateCluster(db, request).execute()
