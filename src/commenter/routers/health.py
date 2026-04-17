from fastapi import APIRouter

from commenter.core.config import settings
from commenter.models.health import HealthResponse

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Returns the current operational status and version of the API.",
)
def health_check() -> HealthResponse:
    return HealthResponse(status="ok", version=settings.app_version)
