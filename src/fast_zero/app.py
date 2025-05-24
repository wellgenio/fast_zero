from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.schemas import (
    MessageSchema,
    TokenSchema,
    UserListSchema,
    UserPublicSchema,
    UserSchema,
)
from fast_zero.scurity import (
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)

app = FastAPI()


@app.get("/", status_code=HTTPStatus.OK, response_model=MessageSchema)
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
    db_user.password = get_password_hash(user.password)

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
    user_id: int,
    user: UserSchema,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
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


@app.delete("/users/{user_id}", status_code=HTTPStatus.NO_CONTENT)
def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="You do not have permission to update this user",
        )

    session.delete(current_user)
    session.commit()


@app.post("/token", response_model=TokenSchema)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    db_user = session.scalar(
        select(User).where(User.email == form_data.username),
    )

    if not db_user or not verify_password(
        form_data.password,
        db_user.password,
    ):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    access_token = create_access_token(
        data={"sub": db_user.email},
    )

    return {"access_token": access_token, "token_type": "Bearer"}
