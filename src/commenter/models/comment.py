from pydantic import BaseModel, Field


class CommentRequest(BaseModel):
    post_title: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="The title of the blog post to comment on",
        examples=["Why Python is Still King in 2026"],
    )
    post_text: str | None = Field(
        default=None,
        min_length=10,
        max_length=50_000,
        description="The full text content of the blog post. If omitted, the crew works from the title only.",
        examples=["Python continues to dominate the AI and data science landscape..."],
    )


class CommentResponse(BaseModel):
    comment: str = Field(
        ...,
        description="The AI-generated comment for the post",
    )
    sources: list[str] = Field(
        default_factory=list,
        description="URLs referenced or used while generating the comment",
    )
    summary: str = Field(
        ...,
        description="One-sentence summary of the comment's stance",
    )
