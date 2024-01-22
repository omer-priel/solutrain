from __future__ import annotations

from uuid import UUID

import psycopg
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from src.models import db_dependency
from src.models.users import Gender, User, create_user, get_user_by_email, validate_email
from src.routers.users import UserSchema
from src.security import create_hash, get_current_user, login_user, logout_user, verify_hash

router = APIRouter()


@router.post("/signup")
async def route_signup(
    name: str,
    email: str,
    password: str,
    phone: str,
    gender: Gender,
    is_trainer: bool,
    is_coach: bool,
    db: psycopg.Connection = Depends(db_dependency),
) -> UserSchema:
    # validation
    if not validate_email(email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email address")

    if get_user_by_email(db, email) is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists with this email")

    # create user
    password_hash = create_hash(password)
    user = create_user(db, name, email, password_hash, phone, gender, is_trainer, is_coach)

    return UserSchema.from_model(user)


class LoginResponseSchema(BaseModel):
    auth_token: UUID
    user: UserSchema


@router.post("/login")
def route_login(email: str, password: str, db: psycopg.Connection = Depends(db_dependency)) -> LoginResponseSchema:
    # validation
    user = get_user_by_email(db, email)

    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="email or password is incorrect")

    if not verify_hash(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="email or password is incorrect")

    # login
    auth_token = login_user(user)

    return LoginResponseSchema(auth_token=auth_token, user=UserSchema.from_model(user))


@router.post("/logout")
def route_logout(auth_token: UUID, current_user: User = Depends(get_current_user)) -> None:
    logout_user(auth_token, current_user)