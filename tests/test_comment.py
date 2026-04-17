from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from commenter.main import app
from commenter.models.comment import CommentResponse

client = TestClient(app)

MOCK_RESPONSE = CommentResponse(
    comment="This is a test comment.",
    summary="Agrees with the post.",
    sources=["https://example.com"],
)


def test_create_comment_success() -> None:
    with patch(
        "commenter.routers.comment.generate_comment",
        new_callable=AsyncMock,
        return_value=MOCK_RESPONSE,
    ):
        response = client.post(
            "/comment/",
            json={
                "post_title": "Test Post",
                "post_text": "This is a test post with enough content to pass validation.",
            },
        )
    assert response.status_code == 200
    data = response.json()
    assert "comment" in data
    assert "summary" in data
    assert "sources" in data


def test_create_comment_title_only() -> None:
    with patch(
        "commenter.routers.comment.generate_comment",
        new_callable=AsyncMock,
        return_value=MOCK_RESPONSE,
    ):
        response = client.post(
            "/comment/",
            json={"post_title": "Test Post — title only"},
        )
    assert response.status_code == 200


def test_create_comment_missing_title() -> None:
    response = client.post(
        "/comment/",
        json={"post_text": "Some content here for validation purposes."},
    )
    assert response.status_code == 422


def test_create_comment_empty_text_treated_as_none() -> None:
    with patch(
        "commenter.routers.comment.generate_comment",
        new_callable=AsyncMock,
        return_value=MOCK_RESPONSE,
    ):
        response = client.post(
            "/comment/",
            json={"post_title": "Test Post", "post_text": ""},
        )
    assert response.status_code == 200
