import uuid
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.config import settings
from app.db.models import User
from app.db.session import get_db
from app.security import create_access_token
from app.services import auth_service

router = APIRouter(prefix="/api/auth")


class RegisterRequest(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=10, max_length=128)
    timezone: str = "Asia/Kolkata"

    @field_validator("timezone")
    @classmethod
    def valid_timezone(cls, v: str) -> str:
        try:
            ZoneInfo(v)
        except Exception:
            raise ValueError("Unknown timezone")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    email: str
    name: str
    timezone: str


@router.post("/register", response_model=TokenResponse)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    if not settings.allow_signup:
        raise HTTPException(status_code=403, detail="Signups are disabled.")
    try:
        user = auth_service.create_user(
            db, email=req.email, name=req.name, password=req.password, timezone=req.timezone
        )
    except auth_service.EmailAlreadyRegistered:
        raise HTTPException(status_code=409, detail="That email is already registered.")
    return TokenResponse(access_token=create_access_token(user.id))


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = auth_service.authenticate(db, email=req.email, password=req.password)
    if user is None:
        # Same message whether the email or the password was wrong.
        raise HTTPException(status_code=401, detail="Incorrect email or password.")
    return TokenResponse(access_token=create_access_token(user.id))


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user