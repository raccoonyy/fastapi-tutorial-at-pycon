import asyncio
import time
from typing import Annotated

import aiofiles
from fastapi import FastAPI, Query
from pydantic import BaseModel, Field, field_validator

app = FastAPI()


@app.get("/hello/{name}")
def hello(
    name: str,
    nickname: Annotated[str, Query(..., min_length=2, max_length=10)]
) -> dict:
    if nickname:
        return {"message": f"Hello {name} ({nickname})"}

    return {"message": f"Hello {name}"}


@app.get("/add")
def add(
    x: Annotated[int, Query(..., ge=0, lt=100)], 
    y: Annotated[int, Query(..., ge=0, lt=100)]
) -> dict:
    return {"result": x + y}


@app.get("/multiply/{x}/{y}")
def multiply(x: int, y: int) -> dict:
    return {"result": x * y}


class User(BaseModel):
    name: str
    age: int
    address: str
    friend_names: list[str]


@app.post("/user")
def create_user(user: User) -> dict:
    return {
        "name": user.name,
        "friens": user.friend_names
    }


class IdSheet(BaseModel):
    filename: str = Field(min_length=1, max_length=10)
    ids: list[int]

    @field_validator('ids')
    def check_ids(cls, ids: list[int]) -> list[int]:
        for id in ids:
            if id <= 0:
                raise ValueError('id는 0보다 커야 해요')

        return sorted(set(ids))


class CreateSheetResponse(BaseModel):
    message: str


@app.post("/sheet", status_code=201, response_model=CreateSheetResponse)
async def create_sheet(sheet: IdSheet):
    start = time.time()
    async with aiofiles.open(sheet.filename, 'w') as f:
        await f.write('id\n')

        for id in sheet.ids:
            asyncio.sleep(1)
            await f.write(f'{id}\n')
    end = time.time() - start
    return {"message": f"created in {end:.2f}s"}
