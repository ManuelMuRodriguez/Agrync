from datetime import datetime
from enum import Enum
from typing import Annotated, Optional
from beanie import Document, Indexed, PydanticObjectId
from pydantic import BaseModel, EmailStr, Field
from utils.datetime import time_at
from beanie.operators import In

class Role(str, Enum):
    admin = "Administrador"
    viewer = "Lector"
    editor = "Editor"

class UserEmail(BaseModel):
    email: EmailStr

class UserName(BaseModel):
    full_name: str

class UserChangePassword(BaseModel):
    password: str
    new_password: str
    new_password_confirmation: str

class UserChangeEmail(BaseModel):
    email: EmailStr
    new_email: EmailStr
    new_email_confirmation: str

class UserAuthForm(UserEmail):
    password: str
    password_confirmation: str

class UserForm(UserEmail, UserName):
    role: Role

class UserByToken(UserName):
    id: PydanticObjectId
    role: Role


#class ShowUser(UserForm):
#    active: bool
#    createdAt: datetime







class User(Document, UserForm):
    email: Annotated[EmailStr, Indexed(unique=True)]
    password: str | None = None
    active: bool = False
    devices: list[str] | None = None
    createdAt: datetime = Field(default_factory=time_at)
    updatedAt: datetime = Field(default_factory=time_at)

    class Settings:
        indexes = [
            "devices",  
        ]

    def __repr__(self) -> str:
        return f"<User {self.email}>"

    def __str__(self) -> str:
        return self.email

    def __eq__(self, other: object) -> bool:
        if isinstance(other, User):
            return self.email == other.email
        return False

    @classmethod
    async def by_email(cls, email: str) -> Optional["User"]:
        """Get a user by email."""
        return await cls.find_one(cls.email == email)

    @classmethod
    async def find_by_device_name(cls, device_name: str) -> list["User"]:
        return await cls.find(In(cls.devices, [device_name])).to_list() 
    






class UserList(UserForm):
    active: bool
    devices: list[str]
    createdAt: datetime
    updatedAt: datetime
    id: PydanticObjectId

class UsersResponseList(BaseModel):
    data: list[UserList]
    totalRowCount: int