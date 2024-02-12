from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel

from src.models.groups import Area, Group, Meet
from src.models.users import Gender, User


class UserBaseSchema(BaseModel):
    user_id: str
    name: str
    email: str
    phone: str
    gender: Gender
    date_of_birth: str

    @staticmethod
    def from_model(user: User) -> UserBaseSchema:
        return UserBaseSchema(
            user_id=str(user.user_id),
            name=user.name,
            email=user.email,
            phone=user.phone,
            gender=user.gender,
            date_of_birth=user.date_of_birth,
        )


class UserSchema(BaseModel):
    """User schema for the API"""

    user_id: str
    name: str
    email: str
    phone: str
    gender: Gender
    date_of_birth: str
    description: str
    is_coach: bool

    @staticmethod
    def from_model(user: User) -> UserSchema:
        return UserSchema(
            user_id=str(user.user_id),
            name=user.name,
            email=user.email,
            phone=user.phone,
            gender=user.gender,
            date_of_birth=user.date_of_birth,
            description=user.description,
            is_coach=user.is_coach,
        )


class AreaSchema(BaseModel):
    area_id: str
    name: str

    @staticmethod
    def from_model(area: Area) -> AreaSchema:
        return AreaSchema(
            area_id=str(area.area_id),
            name=area.name,
        )


class LoginResponseSchema(BaseModel):
    auth_token: UUID
    user: UserSchema
    areas: list[AreaSchema]


class GroupSchema(BaseModel):
    group_id: str
    coach_id: str
    coach_name: str
    name: str
    description: str
    area_id: str

    @staticmethod
    def from_model(group: Group, coach_name: str) -> GroupSchema:
        return GroupSchema(
            group_id=str(group.group_id),
            coach_id=str(group.coach_id),
            coach_name=coach_name,
            name=group.name,
            description=group.description,
            area_id=str(group.area_id),
        )


class GroupInfoSchema(BaseModel):
    group_id: str
    coach_name: str
    name: str
    area_name: str

    @staticmethod
    def from_model(row: tuple[UUID, str, str, str]) -> GroupInfoSchema:
        return GroupInfoSchema(
            group_id=str(row[0]),
            coach_name=row[1],
            name=row[2],
            area_name=row[3],
        )


class MeetSchema(BaseModel):
    meet_id: str
    group_id: str
    max_members: int
    meet_date: str
    duration: int
    city: str
    street: str

    members: list[UserBaseSchema]

    @staticmethod
    def from_model(meet: Meet, members: list[User]) -> MeetSchema:
        return MeetSchema(
            meet_id=str(meet.meet_id),
            group_id=str(meet.group_id),
            max_members=meet.max_members,
            meet_date=str(meet.meet_date),
            duration=meet.duration,
            city=meet.city,
            street=meet.street,
            members=[UserBaseSchema.from_model(member) for member in members],
        )


class MeetInfoSchema(BaseModel):
    meet_id: str
    meet_date: str
    duration: int
    city: str
    street: str
    full: bool
    registered: bool

    @staticmethod
    def from_model(meet: Meet, full: bool, registered: bool) -> MeetInfoSchema:
        return MeetInfoSchema(
            meet_id=str(meet.meet_id),
            meet_date=str(meet.meet_date),
            duration=meet.duration,
            city=meet.city,
            street=meet.street,
            full=full,
            registered=registered,
        )


class GroupViewInfoSchema(BaseModel):
    group: GroupSchema
    meets: list[MeetInfoSchema]


class GroupFullSchema(BaseModel):
    group: GroupSchema
    meets: list[MeetSchema]
    members: list[UserBaseSchema]

    @staticmethod
    def from_model(group: Group, coach_name: str, meets: list[Meet], members: list[User]) -> GroupFullSchema:
        return GroupFullSchema(
            group=GroupSchema.from_model(group, coach_name),
            meets=[MeetSchema.from_model(meet, []) for meet in meets],
            members=[UserBaseSchema.from_model(member) for member in members],
        )


class MyGroupsSchema(BaseModel):
    in_groups: list[GroupInfoSchema]
    coach_groups: list[GroupSchema]


class MyMeetsSchema(BaseModel):
    meets: list[MeetInfoSchema]
