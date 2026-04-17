from fastapi import APIRouter, HTTPException, status

from commenter.agents.crew import generate_comment
from commenter.models.comment import CommentRequest, CommentResponse

router = APIRouter(prefix="/comment", tags=["Comment"])


@router.post(
    "/",
    response_model=CommentResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate a comment for a blog post",
    description=(
        "Accepts a blog post title and body, then runs a multi-agent CrewAI pipeline that:\n\n"
        "1. **Analyzes** the post (thesis, key claims, audience)\n"
        "2. **Researches** related recent data and contrarian viewpoints\n"
        "3. **Forms an opinion** with a clear stance\n"
        "4. **Writes** a concise, opinionated comment with optional supporting URL\n\n"
        "Returns the comment, a one-sentence stance summary, and any sources cited."
    ),
    responses={
        200: {"description": "Comment successfully generated"},
        422: {"description": "Validation error in request body"},
        500: {"description": "Internal error during agent pipeline execution"},
    },
)
async def create_comment(request: CommentRequest) -> CommentResponse:
    try:
        return await generate_comment(request)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent pipeline failed: {exc}",
        ) from exc
