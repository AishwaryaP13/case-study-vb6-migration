from pydantic import BaseModel, field_validator


class LoginInput(BaseModel):
    username: str
    password: str

    @field_validator("username", "password")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("must not be empty")
        return v


class UserOut(BaseModel):
    username: str
    fullname: str | None
    level: str
    is_admin: bool

    model_config = {"from_attributes": True}
