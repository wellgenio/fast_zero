from http import HTTPStatus

from fastapi import FastAPI

from fast_zero.routers import auth, users
from fast_zero.schemas import MessageSchema

app = FastAPI()

app.include_router(users.router)
app.include_router(auth.router)


@app.get("/", status_code=HTTPStatus.OK, response_model=MessageSchema)
def read_root():
    return {"message": "Hello, World!"}
