from datetime import datetime
from fastapi import Body, Path
from pydantic import BaseModel, validator

class LoginData(BaseModel):
    uname: str = Body(...)

    @validator(uname)
    def uname_validator(cls, v):
        assert len(v)>0, "Make sure the username has value"
        return v

    # @validator(password)
    # def password_validator(cls, v):
    #     assert len(v)>0, "Make sure the password has value"
    #     return v