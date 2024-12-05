from uuid import UUID
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, Union, List
from pydantic.types import PositiveInt, PositiveFloat


class CreateClusterRequest(BaseModel):
    name: str
    organization_id: int
    cpu_size: PositiveInt
    ram_size: PositiveFloat
    gpu_size: PositiveFloat


class ListClustersFilters(BaseModel):
    organization_id: Optional[Union[int, List[int]]] = None
    created_at_less_than: Optional[datetime] = None
    created_at_greater_than: Optional[datetime] = None
    updated_at_less_than: Optional[datetime] = None
    updated_at_greater_than: Optional[datetime] = None
    cpu_size_less_than: Optional[PositiveInt] = None
    cpu_size_greater_than: Optional[PositiveInt] = None
    ram_size_less_than: Optional[PositiveFloat] = None
    ram_size_greater_than: Optional[PositiveFloat] = None
    gpu_size_less_than: Optional[PositiveFloat] = None
    gpu_size_greater_than: Optional[PositiveFloat] = None


class ListClustersRequest(BaseModel):
    user_id: UUID
    page: PositiveInt = 1
    page_limit: PositiveInt = 10
    filters: Optional[ListClustersFilters] = None


class UpdateClusterRequest(BaseModel):
    id: UUID
    name: Optional[str] = None
    cpu_size: Optional[PositiveInt] = None
    ram_size: Optional[PositiveFloat] = None
    gpu_size: Optional[PositiveFloat] = None
    status: Optional[str] = None
