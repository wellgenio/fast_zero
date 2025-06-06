from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_zero.database import get_session
from fast_zero.models import Todo, User
from fast_zero.schemas import (
    FilterTodo,
    MessageSchema,
    TodoListSchema,
    TodoPublicSchema,
    TodoSchema,
)
from fast_zero.security import get_current_user

router = APIRouter(prefix="/todos", tags=["todos"])
TSession = Annotated[Session, Depends(get_session)]
TCurrentUser = Annotated[User, Depends(get_current_user)]


@router.post("/", response_model=TodoPublicSchema)
def create_todo(
    todo: TodoSchema,
    user: TCurrentUser,
    session: TSession,
):
    db_todo = Todo(
        title=todo.title,
        description=todo.description,
        state=todo.state,
        user_id=user.id,
    )

    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)
    return db_todo


@router.get("/", response_model=TodoListSchema)
def list_todos(
    session: TSession,
    current_user: TCurrentUser,
    todo_filter: Annotated[FilterTodo, Query()],
):
    query = select(Todo).where(Todo.user_id == current_user.id)

    if todo_filter.title:
        query = query.where(Todo.title.contains(todo_filter.title))

    if todo_filter.description:
        query = query.where(
            Todo.description.contains(todo_filter.description),
        )

    if todo_filter.state:
        query = query.where(Todo.state == todo_filter.state)

    db_todos = session.scalars(
        query.offset(todo_filter.offset).limit(todo_filter.limit)
    ).all()

    return {"todos": db_todos}


@router.put("/{todo_id}", response_model=TodoPublicSchema)
def update_todo(
    todo_id: int,
    todo: TodoSchema,
    session: TSession,
    current_user: TCurrentUser,
):
    db_todo = session.scalar(
        select(Todo).where(
            Todo.user_id == current_user.id,
            Todo.id == todo_id,
        )
    )

    if not db_todo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Task not found.",
        )

    for key, value in todo.model_dump(exclude_unset=True).items():
        setattr(db_todo, key, value)

    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)

    return db_todo


@router.delete("/{todo_id}", response_model=MessageSchema)
def delete_todo(
    todo_id: int,
    session: TSession,
    current_user: TCurrentUser,
):
    db_todo = session.scalar(
        select(Todo).where(
            Todo.user_id == current_user.id,
            Todo.id == todo_id,
        )
    )

    if not db_todo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Task not found.",
        )

    session.delete(db_todo)
    session.commit()
    return {"message": "Task has been deleted successfully."}
