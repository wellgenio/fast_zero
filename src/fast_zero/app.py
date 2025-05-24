from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.schemas import (
    Message,
    UserListSchema,
    UserPublicSchema,
    UserSchema,
)

app = FastAPI()


@app.get("/", status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {"message": "Hello, World!"}


@app.post(
    "/users/",
    status_code=HTTPStatus.CREATED,
    response_model=UserPublicSchema,
)
def create_user(user: UserSchema, session: Session = Depends(get_session)):
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

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@app.get(
    "/users/",
    status_code=HTTPStatus.OK,
    response_model=UserListSchema,
)
def read_users(
    limit: int = 10,
    skip: int = 0,
    session: Session = Depends(get_session),
):
    db_users = session.scalars(
        select(User).limit(limit).offset(skip),
    )
    return {"users": db_users}


@app.put(
    "/users/{user_id}",
    status_code=HTTPStatus.OK,
    response_model=UserPublicSchema,
)
def update_user(
    user_id: int, user: UserSchema, session: Session = Depends(get_session)
):
    db_user = session.get(User, user_id)

    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="User not found",
        )

    db_user.username = user.username
    db_user.email = user.email
    db_user.password = user.password

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@app.delete("/users/{user_id}", status_code=HTTPStatus.NO_CONTENT)
def delete_user(
    user_id: int,
    session: Session = Depends(get_session),
):
    db_user = session.get(User, user_id)

    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="User not found",
        )

    session.delete(db_user)
    session.commit()
