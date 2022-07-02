from datetime import datetime
from fastapi import Body, Path
from pydantic import BaseModel, validator
from typing import List

class LoginData(BaseModel):
    uname: str = Body(...)
    password: str = Body(...)

    @validator('uname')
    def uname_validator(cls, v):
        assert len(v)>0, "Make sure the username has value"
        return v

    @validator('password')
    def password_validator(cls, v):
        assert len(v)>0, "Make sure the password has value"
        return v

class ItemAndCount(BaseModel):
    item: str
    count: int

    @validator('item')
    def uname_validator(cls, v):
        assert len(v)>0, "Make sure the item is valid"
        return v

    @validator('count')
    def password_validator(cls, v):
        assert v>0, "Make sure the qty > 0"
        return v


class Coordinates(BaseModel):
    x: float
    y: float

class NearestStore(BaseModel):
    item_details: List[ItemAndCount]
    user_location: Coordinates

