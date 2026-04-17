import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from commenter.core.config import settings
from commenter.routers import comment_router, health_router

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=settings.app_description,
    contact={
        "name": "Mishka Meirovich",
        "url": "https://github.com/mmeirovich/commenter",
        "email": "mmeirovich@gmail.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=[
        {"name": "Health", "description": "Liveness and readiness probes."},
        {
            "name": "Comment",
            "description": (
                "Generate opinionated, AI-powered comments for blog posts "
                "using a multi-agent CrewAI pipeline."
            ),
        },
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(comment_router)


def run() -> None:
    uvicorn.run(
        "commenter.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    run()
