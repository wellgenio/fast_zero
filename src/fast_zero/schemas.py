from pydantic import BaseModel, ConfigDict, EmailStr


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
