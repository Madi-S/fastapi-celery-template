from pydantic import BaseModel, EmailStr


class UserBody(BaseModel):
    username: str
    email: EmailStr
