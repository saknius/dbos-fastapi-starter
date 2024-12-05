# app/services/deployment/schemas/deployment_schemas.py

from pydantic import BaseModel, validator
from uuid import UUID
from services.deployment.enums.deployment_status import DeploymentStatus

class DeploymentCreate(BaseModel):
    docker_image: str
    required_cpu: int
    required_ram: int
    required_gpu: int
    priority: int
    cluster_id: UUID

    @validator('docker_image')
    def docker_image_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Docker image must not be empty')
        return v

    @validator('required_cpu', 'required_ram')
    def resources_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Resource values must be positive integers')
        return v

    @validator('required_gpu')
    def gpu_must_be_non_negative(cls, v):
        if v < 0:
            raise ValueError('GPU value must be zero or positive integer')
        return v

class DeploymentResponse(BaseModel):
    id: UUID
    docker_image: str
    required_cpu: int
    required_ram: int
    required_gpu: int
    priority: int
    status: DeploymentStatus
    attempts: int
    cluster_id: UUID
    user_id: UUID

    class Config:
        orm_mode = True
