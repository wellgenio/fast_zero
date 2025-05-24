from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.schemas import UserListSchema, UserPublicSchema, UserSchema
from fast_zero.scurity import get_current_user, get_password_hash

router = APIRouter(prefix="/users", tags=["users"])
TSession = Annotated[Session, Depends(get_session)]
TCurrentUser = Annotated[User, Depends(get_current_user)]


@router.post(
    "/",
    status_code=HTTPStatus.CREATED,
    response_model=UserPublicSchema,
)
def create_user(user: UserSchema, session: TSession):
    db_user = session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email),
        ),
    )

    if db_user:
        if db_user.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail="Username already exists",
            )

        if db_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail="Email already exists",
            )

    db_user = User(**user.model_dump())
    db_user.password = get_password_hash(user.password)

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@router.get(
    "/",
    status_code=HTTPStatus.OK,
    response_model=UserListSchema,
)
def read_users(
    session: TSession,
    limit: int = 10,
    skip: int = 0,
):
    db_users = session.scalars(
        select(User).limit(limit).offset(skip),
    )
    return {"users": db_users}


@router.put(
    "/{user_id}",
    status_code=HTTPStatus.OK,
    response_model=UserPublicSchema,
)
def update_user(
    session: TSession,
    user_id: int,
    user: UserSchema,
    current_user: TCurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="You do not have permission to update this user",
        )

    current_user.username = user.username
    current_user.email = user.email
    current_user.password = get_password_hash(user.password)

    session.add(current_user)
    session.commit()
    session.refresh(current_user)

    return current_user


@router.delete("/{user_id}", status_code=HTTPStatus.NO_CONTENT)
def delete_user(
    session: TSession,
    user_id: int,
    current_user: TCurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="You do not have permission to update this user",
        )

    session.delete(current_user)
    session.commit()
