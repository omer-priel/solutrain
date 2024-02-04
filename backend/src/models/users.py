from enum import StrEnum
from uuid import UUID, uuid4

import psycopg

from src.models import db_named_query


class Gender(StrEnum):
    male = "female"
    female = "male"


class User:
    user_id: UUID
    name: str
    email: str
    password_hash: str
    phone: str
    gender: Gender
    description: str
    is_coach: bool

    def __init__(
        self,
        user_id: UUID,
        name: str,
        email: str,
        password_hash: str,
        phone: str,
        gender: Gender,
        description: str,
        is_coach: bool,
    ):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.password_hash = password_hash
        self.phone = phone
        self.gender = gender
        self.description = description
        self.is_coach = is_coach


@db_named_query
def create_user(db: psycopg.Connection, name: str, email: str, password_hash: str, phone: str, gender: Gender, is_coach: bool) -> User:
    user_id = uuid4()
    user = User(
        user_id=user_id,
        name=name,
        email=email,
        password_hash=password_hash,
        phone=phone,
        gender=gender,
        description="",
        is_coach=is_coach,
    )

    with db.cursor() as cursor:
        cursor.execute(
            """INSERT INTO public.users (id, name, email, password_hash, phone, gender, description, is_coach)
            VALUES (%s, %s, %s, %s, %s, %s, %s, True, %s);""",
            (
                str(user.user_id),
                str(user.name),
                str(user.email),
                str(user.password_hash),
                str(user.phone),
                str(user.gender),
                str(user.description),
                bool(user.is_coach),
            ),
        )
        db.commit()

    return user


@db_named_query
def get_user_by_id(db: psycopg.Connection, user_id: UUID) -> User | None:
    with db.cursor() as cursor:
        cursor.execute(
            "SELECT id, name, email, password_hash, phone, gender, description, is_coach FROM users WHERE id = %s",
            [str(user_id)],
        )
        db.commit()

        row = cursor.fetchone()

        if row is None:
            return None

        return User(
            user_id=row[0],
            name=str(row[1]),
            email=str(row[2]),
            password_hash=str(row[3]),
            phone=str(row[4]),
            gender=Gender(str(row[5])),
            description=str(row[6]),
            is_coach=bool(row[7]),
        )


@db_named_query
def get_user_by_email(db: psycopg.Connection, email: str) -> User | None:
    with db.cursor() as cursor:
        cursor.execute(
            "SELECT id, name, email, password_hash, phone, gender, description, is_coach FROM users WHERE email = %s",
            [str(email)],
        )
        db.commit()

        row = cursor.fetchone()

        if row is None:
            return None

        return User(
            user_id=row[0],
            name=str(row[1]),
            email=str(row[2]),
            password_hash=str(row[3]),
            phone=str(row[4]),
            gender=Gender(str(row[5])),
            description=str(row[6]),
            is_coach=bool(row[7]),
        )


@db_named_query
def update_user(
    db: psycopg.Connection, user_id: UUID, updated_name: str, updated_email: str, updated_phone: str, updated_description: str
) -> None:
    with db.cursor() as cursor:
        cursor.execute(
            "UPDATE users SET name = %s, email = %s, phone = %s, description = %s WHERE id = %s",
            [updated_name, updated_email, updated_phone, updated_description, str(user_id)],
        )
        db.commit()


@db_named_query
def update_user_password(db: psycopg.Connection, user_id: UUID, password_hash: str) -> None:
    with db.cursor() as cursor:
        cursor.execute("UPDATE users SET password_hash = %s WHERE id = %s", [password_hash, str(user_id)])
        db.commit()
