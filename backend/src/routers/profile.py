from uuid import UUID

import psycopg
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from starlette import status

from src.models import db_dependency
from src.models.groups import get_coach_groups, get_tariner_groups
from src.models.users import User, get_user_by_email, get_user_by_id, update_user, update_user_password
from src.schemas import GroupInfoSchema, GroupSchema, UserSchema
from src.security import create_hash, get_current_user, update_auth_logged_user_data
from src.validators import validate_email

router = APIRouter(dependencies=[Depends(get_current_user)])


class ProfileSchema(BaseModel):
    user: UserSchema
    is_coach: bool
    in_groups: list[GroupInfoSchema]
    coach_groups: list[GroupSchema]


@router.post("/get")
def route_get(db: psycopg.Connection = Depends(db_dependency), current_user: User = Depends(get_current_user)) -> ProfileSchema:
    in_groups = get_tariner_groups(db, current_user.user_id)
    coach_groups = []

    if current_user.is_coach:
        coach_groups = get_coach_groups(db, current_user.user_id)

    return ProfileSchema(
        user=UserSchema.from_model(current_user),
        is_coach=current_user.is_coach,
        in_groups=[GroupInfoSchema.from_model(row) for row in in_groups],
        coach_groups=[GroupSchema.from_model(group, current_user.name) for group in coach_groups],
    )


@router.post("/update-details")
def route_update_details(
    auth_token: UUID,
    new_name: str | None,
    new_email: str | None,
    new_phone: str | None,
    new_description: str | None,
    db: psycopg.Connection = Depends(db_dependency),
    current_user: User = Depends(get_current_user),
) -> UserSchema:
    updated_name = current_user.name
    updated_email = current_user.email
    updated_phone = current_user.phone
    updated_description = current_user.description

    # validation
    if new_email is not None:
        if not validate_email(new_email):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email")

        if get_user_by_email(db, new_email) is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists with this email")

        updated_email = new_email

    if new_name is not None:
        updated_name = new_name

    if new_phone is not None:
        updated_phone = new_phone

    if new_description is not None:
        updated_description = new_description

    update_user(db, current_user.user_id, updated_name, updated_email, updated_phone, updated_description)

    user = get_user_by_id(db, current_user.user_id)

    if user is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

    update_auth_logged_user_data(auth_token, user)

    return UserSchema.from_model(user)


@router.post("/update-password")
def route_update_password(
    new_password: str, auth_token: UUID, db: psycopg.Connection = Depends(db_dependency), current_user: User = Depends(get_current_user)
) -> UserSchema:
    password_hash = create_hash(new_password)

    update_user_password(db, current_user.user_id, password_hash)

    user = get_user_by_id(db, current_user.user_id)

    if user is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

    update_auth_logged_user_data(auth_token, user)

    return UserSchema.from_model(user)
