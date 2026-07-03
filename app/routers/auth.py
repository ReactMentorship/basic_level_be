"""Auth endpoints: register, login, logout, refresh."""
from fastapi import APIRouter, Depends, HTTPException, status

from ..schemas import LoginBody, RegisterBody
from ..security import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from ..store import users

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(body: RegisterBody):
    if body.username in users:
        raise HTTPException(status.HTTP_409_CONFLICT, "Username already taken")
    users[body.username] = {
        "username": body.username,
        "password": hash_password(body.password),
        "firstname": body.firstname,
        "lastname": body.lastname,
    }
    return {"message": "User registered successfully"}


@router.post("/login")
def login(body: LoginBody):
    user = users.get(body.username)
    if user is None or not verify_password(body.password, user["password"]):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")
    return {"accessToken": create_access_token(user["username"])}


@router.post("/logout")
def logout(_: dict = Depends(get_current_user)):
    # JWTs are stateless; the client just discards its token.
    return {"message": "Logged out successfully"}


@router.post("/refresh")
def refresh(current_user: dict = Depends(get_current_user)):
    # Issue a fresh token; the frontend only reads `message` but the new
    # token is returned too for completeness.
    return {
        "message": "Token refreshed",
        "accessToken": create_access_token(current_user["username"]),
    }
