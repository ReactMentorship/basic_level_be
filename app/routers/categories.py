"""Category endpoints. All require a valid Bearer token."""
from fastapi import APIRouter, Depends, HTTPException, status

from ..schemas import CategoryBody
from ..security import get_current_user
from ..store import categories, new_id, now_iso, posts, serialize_category

router = APIRouter(
    prefix="/categories",
    tags=["categories"],
    dependencies=[Depends(get_current_user)],
)


@router.get("")
def list_categories():
    return [serialize_category(c) for c in categories.values()]


@router.post("", status_code=status.HTTP_201_CREATED)
def create_category(body: CategoryBody):
    ts = now_iso()
    cid = new_id()
    categories[cid] = {
        "_id": cid,
        "name": body.name,
        "createdAt": ts,
        "updatedAt": ts,
        "__v": 0,
    }
    return serialize_category(categories[cid])


@router.patch("/{category_id}")
def update_category(category_id: str, body: CategoryBody):
    cat = categories.get(category_id)
    if cat is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Category not found")
    cat["name"] = body.name
    cat["updatedAt"] = now_iso()
    cat["__v"] += 1
    return serialize_category(cat)


@router.delete("/{category_id}")
def delete_category(category_id: str):
    cat = categories.pop(category_id, None)
    if cat is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Category not found")
    # detach the deleted category from any posts that referenced it
    for post in posts.values():
        if post.get("category_id") == category_id:
            post["category_id"] = None
    return serialize_category(cat)
