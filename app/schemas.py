from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class RegistrationCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    college: str | None = Field(default=None, max_length=150)
    department: str | None = Field(default=None, max_length=150)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Name cannot be empty")
        return value

    @field_validator("college", "department")
    @classmethod
    def clean_optional_fields(cls, value: str | None) -> str | None:
        if value is not None:
            value = value.strip()
            return value or None
        return value

    @field_validator("email")
    @classmethod
    def normalise_email(cls, value: str) -> str:
        return value.strip().lower()


class RegistrationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    college: str | None
    department: str | None
    registered_at: datetime