"""User-facing models. Nothing here talks to the database."""

from datetime import date

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    display_name: str = Field(min_length=1, max_length=80)
    country: str = Field(min_length=2, max_length=2)
    marketing_opt_in: bool = False


class User(BaseModel):
    id: str
    email: EmailStr
    display_name: str
    country: str
    tier: str = "standard"
    marketing_opt_in: bool = False
    joined_on: date | None = None


class UserSummary(BaseModel):
    """The shape routers return in list responses."""

    id: str
    display_name: str
    country: str
    tier: str
