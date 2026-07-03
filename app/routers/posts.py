"""Post endpoints plus the nested "create comment" route. All require auth."""
from fastapi import APIRouter, Depends, HTTPException, Response, status

from ..schemas import CommentBody, PostBody, PostUpdateBody
from ..security import get_current_user
from ..store import (
    categories,
    comments,
    new_id,
    now_iso,
    posts,
    serialize_comment,
    serialize_post,
    serialize_post_detail,
)

router = APIRouter(
    prefix="/posts",
    tags=["posts"],
    dependencies=[Depends(get_current_user)],
)


@router.get("")
def list_posts():
    return [serialize_post(p) for p in posts.values()]


# Declared before /{post_id} so the two-segment path always wins.
@router.get("/category/{category_id}")
def list_posts_by_category(category_id: str):
    return [serialize_post(p) for p in posts.values() if p.get("category_id") == category_id]


@router.get("/{post_id}")
def get_post(post_id: str):
    post = posts.get(post_id)
    if post is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Post not found")
    return serialize_post_detail(post)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_post(body: PostBody):
    category_id = body.category or None
    if category_id and category_id not in categories:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Category does not exist")
    ts = now_iso()
    pid = new_id()
    posts[pid] = {
        "_id": pid,
        "title": body.title,
        "image": body.image,
        "description": body.description,
        "category_id": category_id,
        "comment_ids": [],
        "createdAt": ts,
        "updatedAt": ts,
        "__v": 0,
    }
    return serialize_post(posts[pid])


@router.patch("/{post_id}")
def update_post(post_id: str, body: PostUpdateBody):
    post = posts.get(post_id)
    if post is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Post not found")

    data = body.model_dump(exclude_unset=True)
    if "category" in data:
        category_id = data.pop("category") or None
        if category_id and category_id not in categories:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Category does not exist")
        post["category_id"] = category_id
    for field in ("title", "image", "description"):
        if field in data:
            post[field] = data[field]

    post["updatedAt"] = now_iso()
    post["__v"] += 1
    return serialize_post(post)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: str):
    post = posts.pop(post_id, None)
    if post is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Post not found")
    for cid in post["comment_ids"]:
        comments.pop(cid, None)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{post_id}/comments", status_code=status.HTTP_201_CREATED)
def create_comment(post_id: str, body: CommentBody):
    post = posts.get(post_id)
    if post is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Post not found")
    ts = now_iso()
    cmt_id = new_id()
    comments[cmt_id] = {
        "_id": cmt_id,
        "author": body.author,
        "content": body.content,
        "post_id": post_id,
        "createdAt": ts,
        "updatedAt": ts,
        "__v": 0,
    }
    post["comment_ids"].append(cmt_id)
    post["updatedAt"] = ts
    return serialize_comment(comments[cmt_id])
