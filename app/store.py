"""In-memory data store + helpers that produce the exact JSON shapes the
React frontend expects (Mongo-style ``_id``, ``__v`` and ISO timestamps).

Everything lives in module-level dicts, so all data resets when the server
restarts. That is intentional for a basic-level / development backend.
"""
import secrets
from datetime import datetime, timezone

from . import config

# --- Collections (keyed as noted) ---
users: dict[str, dict] = {}       # keyed by username
categories: dict[str, dict] = {}  # keyed by _id
posts: dict[str, dict] = {}       # keyed by _id
comments: dict[str, dict] = {}    # keyed by _id


def new_id() -> str:
    """Return a 24-char hex string, mimicking a Mongo ObjectId."""
    return secrets.token_hex(12)


def now_iso() -> str:
    """UTC timestamp in the same ISO-8601 format Mongoose emits."""
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


# --- Serializers: turn internal docs into the frontend response shapes ---

def serialize_category(cat: dict) -> dict:
    return {
        "_id": cat["_id"],
        "name": cat["name"],
        "createdAt": cat["createdAt"],
        "updatedAt": cat["updatedAt"],
        "__v": cat["__v"],
    }


def serialize_comment(comment: dict) -> dict:
    return {
        "_id": comment["_id"],
        "author": comment["author"],
        "content": comment["content"],
        "createdAt": comment["createdAt"],
        "updatedAt": comment["updatedAt"],
        "__v": comment["__v"],
    }


def _category_field(post: dict):
    cat = categories.get(post["category_id"]) if post.get("category_id") else None
    return serialize_category(cat) if cat else None


def serialize_post(post: dict) -> dict:
    """List/summary shape: ``comments`` is an array of comment ids."""
    return {
        "_id": post["_id"],
        "title": post["title"],
        "image": post["image"],
        "description": post["description"],
        "category": _category_field(post),
        "comments": list(post["comment_ids"]),
        "createdAt": post["createdAt"],
        "updatedAt": post["updatedAt"],
        "__v": post["__v"],
    }


def serialize_post_detail(post: dict) -> dict:
    """Detail shape: ``comments`` holds full comment objects."""
    data = serialize_post(post)
    data["comments"] = [
        serialize_comment(comments[cid]) for cid in post["comment_ids"] if cid in comments
    ]
    return data


def seed() -> None:
    """Populate the store with a default user and some sample content."""
    from .security import hash_password  # local import to avoid an import cycle

    if users or categories or posts:
        return

    users[config.SEED_USERNAME] = {
        "username": config.SEED_USERNAME,
        "password": hash_password(config.SEED_PASSWORD),
        "firstname": "Admin",
        "lastname": "User",
    }

    ts = now_iso()

    cat_ids: dict[str, str] = {}
    for name in ("Technology", "Travel", "Food"):
        cid = new_id()
        categories[cid] = {"_id": cid, "name": name, "createdAt": ts, "updatedAt": ts, "__v": 0}
        cat_ids[name] = cid

    sample_posts = [
        {
            "title": "Getting started with FastAPI",
            "image": "https://picsum.photos/seed/fastapi/600/400",
            "description": "A quick tour of building REST APIs with FastAPI.",
            "category": "Technology",
        },
        {
            "title": "A weekend in the mountains",
            "image": "https://picsum.photos/seed/mountains/600/400",
            "description": "Trails, fresh air, and great views.",
            "category": "Travel",
        },
        {
            "title": "The perfect homemade pizza",
            "image": "https://picsum.photos/seed/pizza/600/400",
            "description": "Dough, sauce, cheese - the essentials.",
            "category": "Food",
        },
    ]
    for p in sample_posts:
        pid = new_id()
        posts[pid] = {
            "_id": pid,
            "title": p["title"],
            "image": p["image"],
            "description": p["description"],
            "category_id": cat_ids[p["category"]],
            "comment_ids": [],
            "createdAt": ts,
            "updatedAt": ts,
            "__v": 0,
        }

    # one sample comment on the first post
    first_pid = next(iter(posts))
    cmt_id = new_id()
    comments[cmt_id] = {
        "_id": cmt_id,
        "author": "Jane Doe",
        "content": "Great post, thanks for sharing!",
        "post_id": first_pid,
        "createdAt": ts,
        "updatedAt": ts,
        "__v": 0,
    }
    posts[first_pid]["comment_ids"].append(cmt_id)
