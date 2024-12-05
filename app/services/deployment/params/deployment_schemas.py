from typing import Optional
from pydantic import BaseModel
from pydantic.types import UUID, PositiveFloat, PositiveInt


class CreateDeploymentRequest(BaseModel):
    cluster_id: UUID
    docker_image: str
    required_cpu: PositiveInt
    required_ram: PositiveFloat
    required_gpu: PositiveFloat
    priority: Optional[PositiveInt] = None
