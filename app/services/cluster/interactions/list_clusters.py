import logging
from sqlalchemy import select
from fastapi.encoders import jsonable_encoder

from services.cluster.models import Cluster
from services.cluster.params import ListClustersRequest


class ListClusters:

    def __init__(self, db, request):
        self.db = db
        self.query = None
        self.conditions = []
        self.clusters = None
        self.response = None
        self.request = ListClustersRequest(**request)

    def apply_organization_filter(self):
        if self.request.filters.organization_id:
            if isinstance(self.request.filters.organization_id, list):
                self.conditions.append(
                    Cluster.organization_id.in_(self.request.filters.organization_id)
                )
            else:
                self.conditions.append(
                    Cluster.organization_id == self.request.filters.organization_id
                )

    def apply_created_at_filter(self):
        if self.request.filters.created_at_less_than:
            self.conditions.append(
                Cluster.created_at < self.request.filters.created_at_less_than
            )
        if self.request.filters.created_at_greater_than:
            self.conditions.append(
                Cluster.created_at > self.request.filters.created_at_greater_than
            )

    def apply_updated_at_filter(self):
        if self.request.filters.updated_at_less_than:
            self.conditions.append(
                Cluster.updated_at < self.request.filters.updated_at_less_than
            )
        if self.request.filters.updated_at_greater_than:
            self.conditions.append(
                Cluster.updated_at > self.request.filters.updated_at_greater_than
            )

    def apply_cpu_size_filter(self):
        if self.request.filters.cpu_size_less_than:
            self.conditions.append(
                Cluster.cpu_size < self.request.filters.cpu_size_less_than
            )
        if self.request.filters.cpu_size_greater_than:
            self.conditions.append(
                Cluster.cpu_size > self.request.filters.cpu_size_greater_than
            )

    def apply_ram_size_filter(self):
        if self.request.filters.ram_size_less_than:
            self.conditions.append(
                Cluster.ram_size < self.request.filters.ram_size_less_than
            )
        if self.request.filters.ram_size_greater_than:
            self.conditions.append(
                Cluster.ram_size > self.request.filters.ram_size_greater_than
            )

    def apply_gpu_size_filter(self):
        if self.request.filters.gpu_size_less_than:
            self.conditions.append(
                Cluster.gpu_size < self.request.filters.gpu_size_less_than
            )
        if self.request.filters.gpu_size_greater_than:
            self.conditions.append(
                Cluster.gpu_size > self.request.filters.gpu_size_greater_than
            )

    def apply_filters(self):
        if self.request.filters:
            self.apply_organization_filter()
            self.apply_created_at_filter()
            self.apply_updated_at_filter()
            self.apply_cpu_size_filter()
            self.apply_ram_size_filter()
            self.apply_gpu_size_filter()

    def build_query(self):
        self.query = (
            select(Cluster)
            .where(*self.conditions)
            .offset((self.request.page - 1) * self.request.page_limit)
            .limit(self.request.page_limit)
        )

    def run_query(self):
        self.clusters = self.db.scalars(self.query).all()

    def set_response(self):
        self.response = jsonable_encoder(self.clusters)

    def execute(self):
        self.apply_filters()
        self.build_query()
        self.run_query()
        self.set_response()
        return self.response


def list_clusters(db, request):
    return ListClusters(db, request).execute()
