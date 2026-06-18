from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, EmailStr, Field


RoleId = Annotated[int, Field(ge=1, le=3)]
ActiveFlag = Annotated[bool, Field(description="true = active, false = inactive")]


class UserBase(BaseModel):
    full_name: str = Field(min_length=1)
    professional_card: str | None = None
    email: EmailStr
    role_id: RoleId
    firm_id: str | None = None
    status: ActiveFlag = True


class UserPublic(UserBase):
    user_id: str
    created_at: datetime


class UserListResponse(BaseModel):
    items: list[UserPublic]
    page: int
    page_size: int
    total: int


class UserCreateRequest(UserBase):
    password: str = Field(min_length=8)
    status: ActiveFlag = True


class UserUpdateRequest(BaseModel):
    full_name: str | None = Field(default=None, min_length=1)
    professional_card: str | None = None
    role_id: RoleId | None = None
    firm_id: str | None = None
    status: ActiveFlag | None = None


class UserResponse(BaseModel):
    user: UserPublic


class FirmBase(BaseModel):
    name: str = Field(min_length=1)


class FirmPublic(FirmBase):
    firm_id: str
    user_id: str
    created_at: datetime


class CaseBase(BaseModel):
    user_id: str
    firm_id: str | None = None
    name: str = Field(min_length=1)
    legal_area: str = Field(min_length=1)
    status: ActiveFlag = True
    description: str | None = None
    is_public: bool = False


class CasePublic(CaseBase):
    case_id: str
    created_at: datetime
    updated_at: datetime


class DocumentBase(BaseModel):
    case_id: str
    original_filename: str = Field(min_length=1)
    file_type: str = Field(pattern="^(pdf|doc|docx|txt)$")
    file_size_bytes: int = Field(ge=0)
    status: ActiveFlag = True


class DocumentPublic(DocumentBase):
    doc_id: str
    created_at: datetime


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str = Field(min_length=1)
    professional_card: str | None = None
    role_id: RoleId


class RegisterResponse(BaseModel):
    user: UserPublic


class PasswordRecoveryRequest(BaseModel):
    email: EmailStr


class PasswordRecoveryResponse(BaseModel):
    message: str


class PasswordResetRequest(BaseModel):
    token: str = Field(min_length=1)
    new_password: str = Field(min_length=8)


class PasswordResetResponse(BaseModel):
    message: str
