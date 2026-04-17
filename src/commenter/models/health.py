from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(..., description="Service status", examples=["ok"])
    version: str = Field(..., description="API version", examples=["0.1.0"])
