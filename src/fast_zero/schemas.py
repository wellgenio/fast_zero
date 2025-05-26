from pydantic import BaseModel, ConfigDict, EmailStr

from fast_zero.models import TodoState


class MessageSchema(BaseModel):
    message: str


class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserPublicSchema(BaseModel):
    id: int
    username: str
    email: EmailStr
    model_config = ConfigDict(
        from_attributes=True,
    )


class UserListSchema(BaseModel):
    users: list[UserPublicSchema]


class TokenSchema(BaseModel):
    access_token: str
    token_type: str


class FilterPage(BaseModel):
    offset: int = 0
    limit: int = 100


class TodoSchema(BaseModel):
    title: str
    description: str
    state: TodoState


class TodoUpdateSchema(BaseModel):
    title: str | None = None
    description: str | None = None
    state: TodoState | None = None


class TodoPublicSchema(TodoSchema):
    id: int


class TodoListSchema(BaseModel):
    todos: list[TodoPublicSchema]

    model_config = ConfigDict(
        from_attributes=True,
    )


class FilterTodo(FilterPage):
    title: str | None = None
    description: str | None = None
    state: TodoState | None = None
