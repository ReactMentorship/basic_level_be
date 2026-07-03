"""Pydantic request-body models. Responses are built as plain dicts in the
store serializers so we control the exact ``_id`` / ``__v`` keys."""
from pydantic import BaseModel, ConfigDict


class RegisterBody(BaseModel):
    # the frontend also sends firstname/lastname (and a typo variant); ignore extras
    model_config = ConfigDict(extra="ignore")
    username: str
    password: str
    firstname: str | None = None
    lastname: str | None = None


class LoginBody(BaseModel):
    username: str
    password: str


class CategoryBody(BaseModel):
    name: str


class PostBody(BaseModel):
    title: str
    image: str
    description: str
    category: str | None = None  # category _id


class PostUpdateBody(BaseModel):
    title: str | None = None
    image: str | None = None
    description: str | None = None
    category: str | None = None


class CommentBody(BaseModel):
    author: str
    content: str
